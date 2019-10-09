from app.view_models.book import BookViewModel


class MyWishes:
    def __init__(self, wishes_of_mine, wishes_of_wish_count):
        self.wishes = []
        self.__wishes_of_mine = wishes_of_mine
        self.__wishes_of_wish_count = wishes_of_wish_count
        self.wishes = self.__parse()

    def __parse(self):
        temp_list = []
        for wish in self.__wishes_of_mine:
            my_wishes = self.__matching(wish)
            temp_list.append(my_wishes)
        return temp_list

    def __matching(self, wish):
        count = 0
        for wish_count in self.__wishes_of_wish_count:
            if wish.isbn == wish_count['isbn']:
                count = wish_count['count']
        r = {
            'id': wish.id,
            'book': BookViewModel(wish.get_book),
            'wishes_count': count
        }
        return r
