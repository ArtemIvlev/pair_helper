import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('ADMIN_SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модели
class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Pair(db.Model):
    __tablename__ = 'pairs'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# Маршруты
@app.route('/')
@login_required
def dashboard():
    total_users = User.query.count()
    total_pairs = Pair.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_users=total_users,
                         total_pairs=total_pairs,
                         recent_users=recent_users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/users')
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False)
    return render_template('users.html', users=users)

@app.route('/pairs')
@login_required
def pairs():
    page = request.args.get('page', 1, type=int)
    from sqlalchemy.orm import aliased
    
    User1 = aliased(User)
    User2 = aliased(User)
    
    pairs = db.session.query(Pair, User1, User2).join(
        User1, Pair.user1_id == User1.id
    ).join(
        User2, Pair.user2_id == User2.id
    ).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('pairs.html', pairs=pairs)

# Маршруты для управления вопросами
@app.route('/questions')
@login_required
def questions():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', '')
    
    query = Question.query
    if category_filter:
        query = query.filter(Question.category.ilike(f'%{category_filter}%'))
    
    questions = query.order_by(Question.number).paginate(
        page=page, per_page=20, error_out=False)
    
    # Получаем список всех категорий для фильтра
    categories = db.session.query(Question.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('questions.html', 
                         questions=questions, 
                         categories=categories,
                         current_category=category_filter)

@app.route('/questions/add', methods=['GET', 'POST'])
@login_required
def add_question():
    if request.method == 'POST':
        number = request.form['number']
        text = request.form['text']
        category = request.form['category']
        
        # Проверяем, что номер уникален
        existing = Question.query.filter_by(number=int(number)).first()
        if existing:
            flash('Вопрос с таким номером уже существует', 'error')
            return render_template('question_form.html', 
                                 question=None, 
                                 action='add')
        
        question = Question(number=int(number), text=text, category=category)
        db.session.add(question)
        db.session.commit()
        
        flash('Вопрос успешно добавлен', 'success')
        return redirect(url_for('questions'))
    
    return render_template('question_form.html', question=None, action='add')

@app.route('/questions/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        new_number = int(request.form['number'])
        
        # Проверяем уникальность номера (кроме текущего вопроса)
        existing = Question.query.filter(
            Question.number == new_number,
            Question.id != question_id
        ).first()
        
        if existing:
            flash('Вопрос с таким номером уже существует', 'error')
            return render_template('question_form.html', 
                                 question=question, 
                                 action='edit')
        
        question.number = new_number
        question.text = request.form['text']
        question.category = request.form['category']
        question.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Вопрос успешно обновлен', 'success')
        return redirect(url_for('questions'))
    
    return render_template('question_form.html', question=question, action='edit')

@app.route('/questions/delete/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Вопрос успешно удален', 'success')
    return redirect(url_for('questions'))

@app.route('/questions/upload', methods=['GET', 'POST'])
@login_required
def upload_questions():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith(('.xlsx', '.xls')):
            try:
                # Читаем Excel файл
                df = pd.read_excel(file)
                
                # Проверяем наличие необходимых колонок
                required_columns = ['номер', 'вопрос', 'тематика']
                df.columns = df.columns.str.lower().str.strip()
                
                missing_columns = []
                for col in required_columns:
                    if col not in df.columns:
                        missing_columns.append(col)
                
                if missing_columns:
                    flash(f'В файле отсутствуют колонки: {", ".join(missing_columns)}', 'error')
                    return render_template('upload_questions.html')
                
                # Очищаем существующие вопросы
                Question.query.delete()
                
                # Добавляем новые вопросы
                added_count = 0
                for _, row in df.iterrows():
                    if pd.notna(row['номер']) and pd.notna(row['вопрос']) and pd.notna(row['тематика']):
                        question = Question(
                            number=int(row['номер']),
                            text=str(row['вопрос']).strip(),
                            category=str(row['тематика']).strip()
                        )
                        db.session.add(question)
                        added_count += 1
                
                db.session.commit()
                flash(f'Успешно загружено {added_count} вопросов', 'success')
                return redirect(url_for('questions'))
                
            except Exception as e:
                flash(f'Ошибка при обработке файла: {str(e)}', 'error')
                return render_template('upload_questions.html')
        else:
            flash('Пожалуйста, загрузите файл Excel (.xlsx или .xls)', 'error')
    
    return render_template('upload_questions.html')

@app.route('/api/stats')
@login_required
def api_stats():
    total_users = User.query.count()
    total_pairs = Pair.query.count()
    
    # Статистика по дням за последние 30 дней
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    daily_users = db.session.query(
        db.func.date(User.created_at).label('date'),
        db.func.count(User.id).label('count')
    ).filter(
        User.created_at >= thirty_days_ago
    ).group_by(
        db.func.date(User.created_at)
    ).all()
    
    return jsonify({
        'total_users': total_users,
        'total_pairs': total_pairs,
        'daily_users': [{'date': str(day.date), 'count': day.count} for day in daily_users]
    })

if __name__ == '__main__':
    with app.app_context():
        # Удаляем только таблицы админки
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("DROP TABLE IF EXISTS admin_users CASCADE"))
                conn.commit()
        except Exception as e:
            print(f"Ошибка при удалении таблицы admin_users: {e}")
        
        # Создаем только таблицы админки
        AdminUser.__table__.create(db.engine, checkfirst=True)
        Question.__table__.create(db.engine, checkfirst=True)
        
        # Создаем админа по умолчанию если его нет
        if not AdminUser.query.filter_by(username='admin').first():
            admin = AdminUser(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Админ создан: admin / admin123")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
