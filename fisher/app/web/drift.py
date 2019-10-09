from flask import current_app, flash, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_, desc

from app.forms.book import DriftForm
from app.libs.email import send_email
from app.models.base import db
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.user import User
from app.models.wish import Wish
from app.view_models.book import BookViewModel
from app.view_models.drift import DriftCollection
from . import web
from app.libs.enums import PendingStatus


@web.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    current_gift = Gift.query.get_or_404(gid)
    if current_gift.is_yourself_gift(current_user.id):
        flash('这本书是你自己的，不能向自己索要书籍噢')
        return redirect(url_for('web.book_detail', isbn=current_gift.isbn))

    can = current_user.can_send_drift()
    if not can:
        return render_template('not_enough_beans.html', beans=current_user.beans)

    isbn = current_gift.isbn
    repeat_drift = current_user.repeat_drift_count(isbn)
    if not repeat_drift:
        flash('您已经请求过此书，不能重复申请！可在鱼漂中查看！')
        return redirect(url_for('web.book_detail', isbn=isbn))

    drift_form = DriftForm(request.form)
    if request.method == 'POST' and drift_form.validate():
        save_a_drift(drift_form, current_gift)
        try:
            send_email(current_gift.user.email, '有人想要一本书', 'email/get_gift',
                       wisher=current_user,
                       gift=current_gift)
            # 当前拥有礼物的用户邮箱
            flash('邮件发送成功')
            return redirect(url_for('web.pending'))
        except Exception as e:
            print(e)
    gifter = current_gift.user.summary
    return render_template('drift.html', gifter=gifter, user_beans=current_user.beans, form=drift_form)


@web.route('/pending')
@login_required
def pending():
    drifts = Drift.query.filter(or_(Drift.requester_id == current_user.id, Drift.gifter_id ==
                                    current_user.id)).order_by(desc(Drift.create_time)).all()
    views = DriftCollection(drifts, current_user.id)
    return render_template('pending.html', drifts=views.data)


@web.route('/drift/<int:did>/reject')
@login_required
def reject_drift(did):
    with db.auto_commit():
        drift = Drift.query.filter(Gift.uid == current_user.id, Drift.id == did).first_or_404()
        drift.pending = PendingStatus.Reject

        requester = User.query.get_or_404(drift.requester_id)
        requester.beans += 1
    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/redraw')
@login_required
def redraw_drift(did):
    # 撤销最好用javascript
    # 注意超权操作   login_required不足够安全，需要判定是否请求者是否是当前用户
    with db.auto_commit():
        drift = Drift.query.filter(Drift.requester_id == current_user.id, Drift.id == did).first_or_404()
        drift.pending = PendingStatus.Redraw
        current_user.beans += 1
    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/mailed')
def mailed_drift(did):
    # 支持事务 with db.auto_commit() 一致性
    with db.auto_commit():
        drift = Drift.query.filter(Drift.gifter_id == current_user.id, Drift.id == did).first_or_404()
        print(drift)
        drift.pending = PendingStatus.Success
        current_user.beans += 1

        # Gift
        gift = Gift.query.filter_by(id=drift.gifter_id).first_or_404()
        gift.launched = True

        # Wish
        #Wish.query.filter_by(uid=drift.requester_id, isbn=drift.isbn, launch=False).update({Wishlaunched: True})
        wish = Wish.query.filter_by(uid=drift.requester_id, isbn=drift.isbn, launched=False).first_or_404()
        wish.launched = True
    return redirect(url_for('web.pending'))


def save_a_drift(drift_form, current_gift):
    with db.auto_commit():
        book = BookViewModel(current_gift.get_book)

        drift = Drift()
        drift_form.populate_obj(drift)
        drift.gift_id = current_gift.id
        drift.requester_id = current_user.id
        drift.requester_nickname = current_user.nickname
        drift.gifter_nickname = current_gift.user.nickname
        drift.gifter_id = current_gift.user.id
        drift.book_title = book.title
        drift.book_author = book.author
        drift.book_img = book.image
        drift.isbn = book.isbn
        # 当请求生成时，不需要让这个礼物处于锁定状态
        # 这样赠送者是可以收到多个索取请求的，由赠送者选择送给谁
        # current_gift.launched = True
        # 请求者鱼豆-1
        current_user.beans -= 1
        # 但是赠送者鱼豆不会立刻+1
        # current_gift.user.beans += 1
        db.session.add(drift)
