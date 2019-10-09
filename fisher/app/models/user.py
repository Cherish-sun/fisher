from math import floor

from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import Column, ForeignKey, func, and_, or_
from sqlalchemy import String, Unicode, DateTime, Boolean
from sqlalchemy import SmallInteger, Integer, Float
from werkzeug.security import check_password_hash
from sqlalchemy.orm import relationship

from app.libs.enums import PendingStatus
from app.models.base import Base, db
from flask_login import UserMixin, current_user
from app import login_manager
from app.libs.helper import is_key_or_isbn
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.wish import Wish
from spider.YuShu_Book import YuShuBook
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class User(UserMixin, Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    nickname = Column(String(24), nullable=False)
    phone_number = Column(String(18), unique=True)
    email = Column(String(50), unique=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    beans = Column(Float, default=0)
    send_counter = Column(Integer, default=0)
    receive_counter = Column(Integer, default=0)
    # gifts = relationship('Gift')

    _password = Column('password', String(100), nullable=False)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    def cheack_password(self, raw):
        return check_password_hash(self.password, raw)

    # 如果不是id 需要重写get_id,覆盖父类的id
    # def get_id(self):
    #     return self.id
    def can_save_gift_to_list(self, isbn):
        if is_key_or_isbn(isbn) != 'isbn':
            return False
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(isbn)

        if not yushu_book.first:
            return False
        gifting = Gift.query.filter_by(isbn=isbn, uid=self.id, launched=False).first()
        wishing = Wish.query.filter_by(isbn=isbn, uid=self.id, launched=False).first()
        if not gifting and not wishing:
            return True
        else:
            return False

    # 根据SECRET_KEY 和 用户id生成token
    def generate_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def update_pasword_by_token(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        # 如果token是非法的或者过期的抛出异常
        except:
            return False
        user = User.query.get(data.get('id'))
        if user is None:
            return False
        with db.auto_commit():
            user.password = new_password
        return True

    def can_send_drift(self, current_gift_id=None):
        if current_gift_id:
            gift = Gift.query.get(current_gift_id)
            if gift.uid == self.id:
                return False
        if self.beans < 1:
            return False
        # success_send_gift_count = Gift.query.filter(uid=self.id, launched=True).count()
        success_send_gift_count = Drift.query.filter(Drift.pending == PendingStatus.Success,
                                                     Gift.uid == self.id).count()
        success_receive_gift_count = Drift.query.filter(Drift.pending == PendingStatus.Success,
                                                        Drift.requester_id == self.id).count()
        return True if floor(success_send_gift_count / 2) <= floor(success_receive_gift_count) else False

    def repeat_drift_count(self, isbn):
        # 同一个请求者不能对同一书籍重复请求
        repeat_status = Drift.query.filter(
            and_(Drift.requester_id == self.id, Drift._pending == PendingStatus.Waiting.value
                 , Drift.isbn == isbn)).count()
        return True if repeat_status < 1 else False

    @property
    def summary(self):
        return dict(
            nickname=self.nickname,
            beans=self.beans,
            email=self.email,
            send_receive=str(self.send_counter) + '/' + str(self.receive_counter)
        )


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
