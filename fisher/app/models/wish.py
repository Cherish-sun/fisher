from app.models.base import Base, db
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship

from spider.YuShu_Book import YuShuBook


class Wish(Base):
    __tablename__ = 'wish'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User')
    isbn = Column(String(13))
    # 礼物是否赠出
    launched = Column(Boolean, default=False)

    @classmethod
    def get_user_wishes(cls, uid):
        wishes = Wish.query.filter_by(uid=uid, launched=False).all()
        return wishes

    @classmethod
    def get_wish_count(cls, wishes_list_isbn):
        # 计算出Gift表中某个礼物的赠送数量
        count_list = db.session.query(func.count(Gift.id), Gift.isbn).filter(Gift.launched == False,
                                                                             Gift.isbn.in_(wishes_list_isbn),
                                                                             Gift.status == 1).group_by(Gift.isbn).all()

        count_list = [{'count': word[0], 'isbn': word[1]} for word in count_list]
        return count_list

    @property
    def get_book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first


from app.models.gift import Gift
