from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import os
from flask_login import login_required, current_user
from agriplatform.forms.forum_form import NewPostForm

forum_bp = Blueprint('forum', __name__)
DB_PATH = os.path.join("agriplatform", "agriconnect.db")

# helper to get db connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# view all posts
@forum_bp.route('/forum')
def forum_home():
    conn = get_db_connection()
    posts = conn.execute('SELECT forum_posts.*, users.username FROM forum_posts JOIN users ON forum_posts.user_id = users.id ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('forum/forum.html', posts=posts)

#new posts and submission
@forum_bp.route('/forum/new', methods=['GET', 'POST'])
def new_post():
    form = NewPostForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        conn = get_db_connection()
        conn.execute('INSERT INTO forum_posts (user_id, title, content) VALUES (?, ?, ?)',
                     (current_user.id, title, content))
        conn.commit()
        conn.close()
        return redirect(url_for('forum.forum_home'))
    return render_template('forum/new_post.html', form=form)
