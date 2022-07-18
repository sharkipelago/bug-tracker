from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from bugstar import admin

from bugstar.auth import login_required
from bugstar.admin import admin_required
from bugstar.db import get_db

bp = Blueprint('feed', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()

    issues = db.execute(
        'SELECT closer_id, created, title, body, author_id, i.id,'
        ' (firstname || " " || lastname) AS authorname'
        f' FROM issues i'
        ' JOIN users u ON i.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    


    return render_template('feed/index.html', issues=issues, assignees=get_assignees(), user=g.user)
    
def get_assignees(id=-1):
#if no id is provided or -1 is passed assignees will reutrn all assignees in the database.
# Otherwise it will return just the assignees of a particular id provided
    if id < -1 or not isinstance(id, int):
        return

    db = get_db()
    if id == -1:
        assignees_query = db.execute(
            'SELECT a.*, (firstname || " " || lastname) AS name'
            ' FROM assignments a'
            ' JOIN users u ON a.assignee_id = u.id'
        ).fetchall()
    
        #dictionary where the key is an issue id and the value is a list of assigne objects with a id and name property
        assignees = {}
        
        for row in assignees_query:
            i_id = row["issue_id"]
            if i_id not in assignees:  
                assignees[i_id] = []
            assignees[i_id].append({
                "id": row["assignee_id"],
                "name": row["name"]
            })

    else:
        assignees_query = db.execute(
            'SELECT a.*, (firstname || " " || lastname) AS name'
            ' FROM assignments a'
            ' JOIN users u ON a.assignee_id = u.id'
            ' WHERE a.issue_id = ?',
            (id,)
        ).fetchall()
    
        #list of assigne objects with a id and name property
        assignees = []
        
        for row in assignees_query:
            assignees.append({
                "id": row["assignee_id"],
                "name": row["name"]
            })
     
    return assignees

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@admin_required
def create():
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        assignees =  request.form.getlist('assignees')
        
        error = None

        if not title:
            error = 'Title is required.'

        if not assignees:
            error = "At least one assignee is required."

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO issues (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            issue_id = db.execute(
                'SELECT i.id'
                ' FROM issues i'
                ' WHERE title = ?'
                ' ORDER BY created DESC',
                (title, )
            ).fetchone()['id']
            for assignee in assignees:
                db.execute(
                    'INSERT INTO assignments (issue_id, assignee_id)'
                    ' VALUES (?, ?)',
                    (issue_id, assignee)
                )
            db.commit()
            return redirect(url_for('index'))

    

    return render_template('feed/create.html', user=g.user, all_users=get_all_users())

def get_issue(id, check_author=True):
    issue = get_db().execute(
        'SELECT i.id, title, body, created, author_id, username'
        ' FROM issues i' 
        ' JOIN users u ON i.author_id = u.id'
        ' WHERE i.id = ?',
        (id,)
    ).fetchone()

    if issue is None:
        abort(404, f"issue id {id} doesn't exist.")

    if check_author and issue['author_id'] != g.user['id']:
        abort(403)

    return issue

def get_all_users():
    return  get_db().execute(
        'SELECT id, (firstname || " " || lastname) AS name'
        ' FROM users'
        ' ORDER BY lastname'
    ).fetchall()

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
@admin_required
def update(id):
    issue = get_issue(id)
    assignees = get_assignees(id)
    assigned_ids = []
    for a in assignees:
        assigned_ids.append(a["id"])

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_assignees =  request.form.getlist('assignees')

        error = None

        if not title:
            error = 'Title is required.'

        if not new_assignees:
            error = "At least one assignee is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE issues SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )

            #Deleting old assignees from the issue
            for og in assigned_ids:
                if og in  new_assignees:
                    continue
                db.execute(
                    'DELETE FROM assignments WHERE issue_id = ? AND assignee_id = ?', (id, og)
                )

            #Adding new assignees to the issue
            for new in new_assignees:
                if new in assigned_ids:
                    continue
                db.execute(
                    'INSERT INTO assignments (issue_id, assignee_id)'
                    ' VALUES (?, ?)',
                    (id, new)
                )
            db.commit()
            return redirect(url_for('feed.index'))

    return render_template('feed/update.html', user=g.user, issue=issue, assigned_ids=assigned_ids, all_users=get_all_users())

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
@admin_required
def delete(id):
    get_issue(id)
    db = get_db()
    db.execute('DELETE FROM issues WHERE id = ?', (id,))
    db.execute('DELETE FROM assignments WHERE issue_id = ?', (id,))
    db.commit()
    return redirect(url_for('feed.index'))