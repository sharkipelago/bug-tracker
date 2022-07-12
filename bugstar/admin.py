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


@bp.route('/denied')
@login_required
def denied():
    return render_template('admin/denied.html', user=g.user)

