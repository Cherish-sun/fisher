from flask_login import current_user

from app.models.base import db
from app.models.gift import Gift
from app.models.wish import Wish
from app.view_models.trade import MyTrades
from app.view_models.wish import MyWishes
from . import web
from flask_login import login_required, current_user
from flask import current_app, flash, redirect, url_for, render_template
from app.libs.email import send_email


@web.route('/my/wish')
def my_wish():
    # 我想要的书籍
    uid = current_user.id
    wishes_of_mine = Wish.get_user_wishes(uid)
    # 我想要的书籍的isbn存入列表
    wishes_list_isbn = [wish.isbn for wish in wishes_of_mine]
    # 根据isbn从Gift里查询每本书想要的人数
    wishes_of_wish_count = Wish.get_wish_count(wishes_list_isbn)
    # 格式化 数据
    # wish_model = MyWishes(wishes_of_mine, wishes_of_wish_count)
    wish_model = MyTrades(wishes_of_mine, wishes_of_wish_count)
    return render_template('my_wish.html', wishes=wish_model.trades)


@web.route('/wish/book/<isbn>')
def save_to_wish(isbn):
    if current_user.can_save_gift_to_list(isbn):
        # 事务 只要使用db.session 都要使用rollback
        with db.auto_commit():
            wish = Wish()
            wish.isbn = isbn
            wish.uid = current_user.id
            db.session.add(wish)
    else:
        flash('您已将此书加入心愿清单不能重复加入！')
    return redirect(url_for('web.book_detail', isbn=isbn))


@web.route('/satisfy/wish/<int:wid>')
@login_required
def satisfy_wish(wid):
    wish = Wish.query.get_or_404(wid)
    gift = Gift.query.filter_by(uid=current_user.id, isbn=wish.isbn).first()
    if not gift:
        flash('你还没有上传此书，请点击“加入到赠送清单”添加此书。添加前，请确保自己可以赠送此书')
    else:
        send_email(wish.user.email, '有人想送你一本书', 'email/satisify_wish', wish=wish,
                   gift=gift)
        flash('已向他/她发送了一封邮件，如果他/她愿意接受你的赠送，你将收到一个鱼漂')
    return redirect(url_for('web.book_detail', isbn=wish.isbn))


# 撤销心愿
@web.route('/wish/book/<isbn>/redraw')
@login_required
def redraw_from_wish(isbn):
    wish = Wish.query.filter_by(isbn=isbn, launched=False, uid=current_user.id).first()
    if not wish:
        flash('该心愿不存在，删除失败')
    with db.auto_commit():
        wish.delete()
    return redirect(url_for('web.my_wish'))
