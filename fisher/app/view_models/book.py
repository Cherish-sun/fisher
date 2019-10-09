class BookViewModel:
    def __init__(self, data):
        self.title = data['title']
        self.author = '、'.join(data['author'])
        self.binding = data['binding']
        self.publisher = data['publisher']
        self.image = data['image']
        self.price = data['price']
        self.isbn = data['isbn']
        self.pubdate = data['pubdate']
        self.summary = data['summary']
        self.pages = data['pages']

    @property
    def intro(self):
        intro = filter(lambda x: True if x else False, [self.author, self.publisher, self.price])
        return ' / '.join(intro)


class BookCollection:
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = ''

    def fill(self, yushu_book, keyword):
        self.total = yushu_book.total
        self.books = [BookViewModel(book) for book in yushu_book.books]
        self.keyword = keyword


# class _ViewModel:
#
#     @classmethod
#     def package_single_isbn(cls, keyword, data):
#
#         returned = {
#             'total': 0,
#             'keyword': keyword,
#             'books': []
#         }
#         if data:
#             returned['total'] = 1
#             returned['books'] = [cls.__cut_book_data(data)]
#             return returned
#
#     @classmethod
#     def package_collection_key(cls, keyword, data):
#         returned = {
#             'total': 0,
#             'keyword': keyword,
#             'books': []
#         }
#         if data:
#             returned['books'] = [cls.__cut_book_data(d) for d in data['books']]
#             returned['total'] = data['total']
#             return returned
#
#     @classmethod
#     def __cut_book_data(cls, data):
#         book = {'title': data['title'],
#                 'author': '、'.join(data['author']),
#                 'binding': data['binding'],
#                 'publisher': data['publisher'],
#                 'image': data['images']['large'],
#                 'price': data['price'] or '',
#                 'isbn': data['isbn'],
#                 'pubdate': data['pubdate'],
#                 'summary': data['summary'] or '',
#                 'pages': data['pages'] or ''
#                 }
#         return book
