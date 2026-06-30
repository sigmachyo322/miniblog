from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ─── Models ──────────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# ─── Auth helper ─────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Войдите, чтобы продолжить.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


app.jinja_env.globals['current_user'] = current_user


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def post_create():
    if request.method == 'POST':
        title = request.form['title'].strip()
        body = request.form['body'].strip()
        if not title or not body:
            flash('Заполните все поля.', 'danger')
        else:
            post = Post(title=title, body=body, user_id=session['user_id'])
            db.session.add(post)
            db.session.commit()
            flash('Статья опубликована!', 'success')
            return redirect(url_for('post_detail', post_id=post.id))
    return render_template('post_form.html', post=None)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def post_edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        flash('Нет прав на редактирование.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        post.title = request.form['title'].strip()
        post.body = request.form['body'].strip()
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Статья обновлена!', 'success')
        return redirect(url_for('post_detail', post_id=post.id))
    return render_template('post_form.html', post=post)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        flash('Нет прав на удаление.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Статья удалена.', 'info')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Заполните все поля.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято.', 'danger')
        elif len(password) < 6:
            flash('Пароль должен быть минимум 6 символов.', 'danger')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            flash(f'Добро пожаловать, {username}!', 'success')
            return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f'Привет, {username}!', 'success')
            return redirect(url_for('index'))
        flash('Неверные данные.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


@app.route('/my-posts')
@login_required
def my_posts():
    posts = Post.query.filter_by(user_id=session['user_id']).order_by(Post.created_at.desc()).all()
    return render_template('my_posts.html', posts=posts)


# ─── Init DB ─────────────────────────────────────────────────────────────────

def seed_db():
    """Create demo user and posts if DB is empty."""
    if User.query.count() == 0:
        demo = User(username='admin')
        demo.set_password('admin123')
        db.session.add(demo)
        db.session.flush()
        posts = [
            Post(title='Добро пожаловать в MiniBlog!',
                 body='Это демо-статья. Войдите как admin / admin123 чтобы редактировать или создавать новые публикации.',
                 user_id=demo.id),
            Post(title='Как пользоваться блогом',
                 body='Зарегистрируйтесь или войдите — и вы сможете публиковать собственные статьи, редактировать и удалять их.',
                 user_id=demo.id),
        ]
        db.session.add_all(posts)
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
