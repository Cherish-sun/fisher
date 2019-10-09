from app.libs.httper import Http
from flask import current_app


class YuShuBook:
    isbn_url = 'http://t.yushu.im/v2/book/isbn/{}'
    # keyword_url = 'http://t.yushu.im/v2/book/search?q={}&count={}&start={}'
    keyword_url = 'http://t.yushu.im/v2/book/search?q={}'

    def __init__(self):
        self.total = 0
        self.books = []

    @property
    def get_book(self):
        books = self.books[0] if self.total >= 1 else None
        return books

    def search_by_keyword(self, q, page=1):
        #key = self.keyword_url.format(q, current_app.config['PER_PAGE'], self.calculate_start(page))
        key = self.keyword_url.format(q)
        result = Http.get(key)
        self.__keyword(result)

    def search_by_isbn(self, q):
        isbn = self.isbn_url.format(q)
        result = Http.get(str(isbn))
        self.__isbn(result)

    def __keyword(self, data):
        self.total = data['total']
        self.books = data['books']

    def __isbn(self, data):
        if data:
            self.total = 1
            self.books.append(data)

    def calculate_start(self, page):
        return (page - 1) * current_app.config['PER_PAGE']

    @property
    def first(self):
        return self.books[0] if self.total >= 1 else None
