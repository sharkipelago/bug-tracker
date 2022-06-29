from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from bugstar.auth import login_required
from bugstar.db import get_db

bp = Blueprint('feed', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    issues = db.execute(
        'SELECT i.id, author_id, closer_id, created, title, body, (firstname || " " || lastname) AS authorname'
        ' FROM issue i JOIN user u ON i.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('feed/index.html', issues=issues, user=g.user)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO issue (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('feed/create.html', user=g.user)

def get_issue(id, check_author=True):
    issue = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM issue p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if issue is None:
        abort(404, f"issue id {id} doesn't exist.")

    if check_author and issue['author_id'] != g.user['id']:
        abort(403)

    return issue

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    issue = get_issue(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE issue SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('feed.index'))

    return render_template('feed/update.html', issue=issue)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_issue(id)
    db = get_db()
    db.execute('DELETE FROM issue WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('feed.index'))