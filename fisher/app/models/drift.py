# from app.libs.enums import PendingStatus
from sqlalchemy import Column, String, Integer, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship

from app.libs.enums import PendingStatus
from app.models.base import Base


class Drift(Base):
    """
        一次具体的交易信息
    """
    __tablename__ = 'drift'

    # def __init__(self):
    #     self.pending = PendingStatus.waiting
    #     super(Drift, self).__init__()

    id = Column(Integer, primary_key=True)
    recipient_name = Column(String(20), nullable=False)
    address = Column(String(100), nullable=False)
    message = Column(String(200))
    mobile = Column(String(20), nullable=False)
    # 书籍信息
    isbn = Column(String(13))
    book_title = Column(String(50))
    book_author = Column(String(30))
    book_img = Column(String(50))
    # requester_id = Column(Integer, ForeignKey('user.id'))
    # requester = relationship('User')
    # 请求者 具有记录性质的字段，不要关联
    requester_id = Column(Integer)
    requester_nickname = Column(String(20))
    # 赠送者
    gifter_id = Column(Integer)
    gift_id = Column(Integer)
    gifter_nickname = Column(String(20))
    _pending = Column('pending', SmallInteger, default=1)

    # 读取_pending 时转化为枚举

    @property
    def pending(self):
        return PendingStatus(self._pending)

    # gift_id = Column(Integer, ForeignKey('gift.id'))
    # gift = relationship('Gift')

    # status 是枚举类型 要把枚举转化为数字
    @pending.setter
    def pending(self, status):
        self._pending = status.value
