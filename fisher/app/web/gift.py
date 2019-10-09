from app.libs.enums import PendingStatus
from app.models.drift import Drift
from app.view_models.gift import MyGifts
from app.view_models.trade import MyTrades
from . import web
from flask_login import login_required, current_user
from app.models.gift import Gift
from app.models.base import db
from flask import flash, current_app, redirect, url_for, render_template


@web.route('/my/gifts')
@login_required
def my_gifts():
    uid = current_user.id
    # 查询出我的礼物
    gifts_of_mine = Gift.get_user_gifts(uid)
    # 查询出我的礼物isbn，列表
    gifts_list_isbn = [gift.isbn for gift in gifts_of_mine]
    # 根据礼物的isbn，查询出每个礼物对应的加入心愿数量
    gifts_of_gift_count = Gift.get_wish_count(gifts_list_isbn)
    # view_model = MyGifts(gifts_of_mine, gifts_of_gift_count)
    # 将 MyGifts 和 MyWishes封装成MyTrades
    view_model = MyTrades(gifts_of_mine, gifts_of_gift_count)
    return render_template('my_gifts.html', gifts=view_model.trades)


@web.route('/gifts/book/<isbn>')
@login_required
# 赠送此书 current_user 实际上是用户模型的对象
def save_to_gifts(isbn):
    if current_user.can_save_gift_to_list(isbn):
        # 事务 只要使用db.session 都要使用rollback
        with db.auto_commit():
            gift = Gift()
            gift.isbn = isbn
            gift.uid = current_user.id
            current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
            db.session.add(gift)

    else:
        flash('您已赠送过此书不能重复赠送！')
    return redirect(url_for('web.book_detail', isbn=isbn))


@web.route('/gifts/<gid>/redraw')
@login_required
def redraw_from_gifts(gid):
    gift = Gift.query.filter_by(uid=current_user.id, id=gid, launched=False).first_or_404()
    drift = Drift.query.filter_by(gift_id=gid, pending=PendingStatus.Waiting).first()
    if drift:
        flash('请完成鱼漂中的交易，才能撤销')
    else:
        with db.auto_commit():
            current_user.beans -= current_app.config['BEANS_UPLOAD_ONE_BOOK']
            gift.delete()
        return redirect(url_for('web.my_gifts'))
