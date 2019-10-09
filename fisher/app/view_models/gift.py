from collections import namedtuple

from app.view_models.book import BookViewModel


# MyGift = namedtuple('MyGift', ['id', 'isbn', 'wishes_count'])

class MyGifts:
    def __init__(self, wishes_of_mine, wishes_of_gift_count):
        self.gifts = []
        self.__wishes_of_mine = wishes_of_mine
        self.__wishes_of_gift_count = wishes_of_gift_count
        # 不建议直接修改实例属性，可以读取使用
        self.gifts = self.__parse()

    def __parse(self):
        temp_list = []
        for gift in self.__wishes_of_mine:
            # 根据每个gift， 获取收藏数
            my_gift = self.__map_gifts(gift)
            temp_list.append(my_gift)
        return temp_list

    def __map_gifts(self, wish):
        count = 0

        for wish_count in self.__wishes_of_gift_count:
            if wish.isbn == wish_count['isbn']:
                count = wish_count['count']
        # my_gift = MyGift(gift.id, BookViewModel(gift.get_book), count)
        # return my_gift
        r = {
            'id': wish.id,
            'book': BookViewModel(wish.get_book),
            'wishes_count': count
        }
        return r
