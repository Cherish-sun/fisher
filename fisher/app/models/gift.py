from app.models.base import Base, db
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, desc, func
from sqlalchemy.orm import relationship
from flask import current_app

from spider.YuShu_Book import YuShuBook


class Gift(Base):
    __tablename__ = 'gift'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User')
    isbn = Column(String(13))
    # 礼物是否赠出
    launched = Column(Boolean, default=False)

    # 对象代表一个礼物，具体存在
    # 类代表礼物这个事物，它是抽象
    @classmethod
    def recent(cls):
        recent_gifts = Gift.query.filter_by(launched=False).group_by(Gift.isbn).order_by(
            desc(Gift.create_time)).limit(
            current_app.config['RECENT_BOOK']
        ).distinct().all()
        return recent_gifts

    @property
    def get_book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def get_user_gifts(cls, uid):
        gift = Gift.query.filter_by(uid=uid, launched=False).all()
        return gift

    @classmethod
    def get_wish_count(cls, isbn_list):
        # 计算出Wish表中某个礼物的心愿数量
        count_list = db.session.query(func.count(Wish.id), Wish.isbn).filter(Wish.launched == False,
                                                                             Wish.isbn.in_(isbn_list),
                                                                             Wish.status == 1).group_by(Wish.isbn).all()

        count_list = [{'count': word[0], 'isbn': word[1]} for word in count_list]
        return count_list

    # 自己不能向自己请求书籍
    def is_yourself_gift(self, uid):
        return True if self.uid == uid else False


from app.models.wish import Wish
