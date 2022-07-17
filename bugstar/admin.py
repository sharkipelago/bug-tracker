import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from bugstar.auth import login_required
from bugstar.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Must be admin to access view
def admin_required(view): 
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user["is_admin"] == 0:
            return redirect(url_for('admin.denied'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/')
@admin_required
@login_required
def index():
    db = get_db()
    users = db.execute(
        'SELECT * FROM users'
    ).fetchall()

    return render_template('admin/manage-users.html', users=users, user=g.user)

@bp.route('/<int:id>/promote', methods=('POST',))
@admin_required
@login_required
def promote(id):
    db = get_db()
    db.execute(
        'UPDATE users SET is_admin = 1'
        ' WHERE id = ?',
        (id,)
    )
    db.commit()
    return redirect(url_for('admin.index'))

@bp.route('/<int:id>/remove', methods=('POST',))
@admin_required
@login_required
def remove(id):
    db = get_db()
    assignments = db.execute(
        'SELECT * FROM assignments'
        ' WHERE assignee_id = ?',
        (id,)
    ).fetchone()
    error = None

    if assignments:
        error = "User must be removed from all issues before being deleted"

    #This means this user is not in the assignments table so we can simply delete them from users
    if error is None:
        db.execute(
            'DELETE FROM users WHERE id = ?', (id,)
        )

        #If the user closed any issues set the closer id to -1 to represent a deleted user
        db.execute(
            'UPDATE issues SET closer_id = -1'
            ' WHERE closer_id = ?', (id, )
        )
        db.commit()
    else:
        flash(error)
        
    return redirect(url_for('admin.index'))



@bp.route('/denied')
@login_required
def denied():
    return render_template('admin/denied.html', user=g.user)

