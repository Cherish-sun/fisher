from . import web
from app.models.gift import Gift
from flask import render_template
from app.view_models.book import BookViewModel


@web.route('/')
def index():
    recent_gift = Gift.recent()
    books = [BookViewModel(gift.get_book) for gift in recent_gift]
    return render_template('index.html', recent=books)


@web.route('/personal')
def personal_center():
    pass
