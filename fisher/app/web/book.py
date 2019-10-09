from flask import jsonify, request, render_template, flash
from app.libs.helper import is_key_or_isbn
from app.models.gift import Gift
from app.models.wish import Wish
from app.view_models.trade import TradeInfo
from spider.YuShu_Book import YuShuBook
from app.forms.book import SearchForm
# from app.web import web
from . import web
from app.view_models.book import BookViewModel, BookCollection
from flask_login import current_user


@web.route('/book/search')
def search():
    # r = request.args.get('q')
    # q = request.args['q']
    # page = request.args['page']
    form = SearchForm(request.args)
    books = BookCollection()
    if form.validate():
        q = form.q.data.strip()
        page = form.page.data
        key_or_isbn = is_key_or_isbn(q)
        yushu_books = YuShuBook()
        if key_or_isbn == 'key':
            yushu_books.search_by_keyword(q, page)
            # result = YuShuBook.search_by_keyword(q, page)
        else:
            # result = YuShuBook.search_by_isbn(q)
            yushu_books.search_by_isbn(q)
        books.fill(yushu_books, q)
        # return json.dumps(books, default=lambda o: o.__dict__)

    else:
        flash('请输入合理的关键字!')
    return render_template('search_result.html', books=books)


@web.route('/book/<isbn>/detail')
def book_detail(isbn):
    # 默认既不在心愿清单和礼物清单
    has_in_gifts = False
    has_in_wishes = False

    # 获取书籍详情
    yushu_books = YuShuBook()
    yushu_books.search_by_isbn(isbn)
    books = BookViewModel(yushu_books.get_book)
    if current_user.is_authenticated:
        if Gift.query.filter_by(uid=current_user.id, isbn=isbn,
                                launched=False).first():
            has_in_gifts = True
        if Wish.query.filter_by(uid=current_user.id, isbn=isbn,
                                launched=False).first():
            has_in_wishes = True

    # 查询当前isbn的礼物清单和心愿清单
    trade_gift = Gift.query.filter_by(isbn=isbn, launched=False).all()
    trade_wish = Wish.query.filter_by(isbn=isbn, launched=False).all()

    gift_model = TradeInfo(trade_gift)
    wish_model = TradeInfo(trade_wish)
    # 处理数据
    return render_template('book_detail.html', book=books, wishes=wish_model, gifts=gift_model,
                           has_in_gifts=has_in_gifts,
                           has_in_wishes=has_in_wishes)
