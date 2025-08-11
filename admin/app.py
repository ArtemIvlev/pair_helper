import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import Enum as SAEnum


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('ADMIN_SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Маршруты обратной связи
@app.route('/feedback')
@login_required
def feedback_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Фильтры
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    
    # Преобразуем значения для фильтрации
    if status_filter:
        status_filter = status_filter.lower()
    if type_filter:
        type_filter = type_filter.lower()
    
    query = Feedback.query.join(User)
    
    if status_filter:
        # Используем ILIKE для регистронезависимого поиска
        query = query.filter(db.func.lower(Feedback.status) == status_filter)
    if type_filter:
        # Используем ILIKE для регистронезависимого поиска
        query = query.filter(db.func.lower(Feedback.feedback_type) == type_filter)
    
    feedback = query.order_by(Feedback.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Статистика с преобразованием значений
    def normalize_status(status):
        return status.lower() if status else ''
    
    def normalize_type(feedback_type):
        return feedback_type.lower() if feedback_type else ''
    
    all_feedback = Feedback.query.all()
    stats = {
        'total': len(all_feedback),
        'new': len([f for f in all_feedback if normalize_status(f.status) == 'new']),
        'in_progress': len([f for f in all_feedback if normalize_status(f.status) == 'in_progress']),
        'resolved': len([f for f in all_feedback if normalize_status(f.status) == 'resolved']),
        'closed': len([f for f in all_feedback if normalize_status(f.status) == 'closed']),
    }
    
    return render_template('feedback.html', 
                         feedback=feedback, 
                         stats=stats,
                         status_filter=status_filter,
                         type_filter=type_filter)

@app.route('/feedback/<int:feedback_id>')
@login_required
def feedback_detail(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    return render_template('feedback_detail.html', feedback=feedback)

@app.route('/feedback/<int:feedback_id>/update', methods=['POST'])
@login_required
def feedback_update(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    
    status = request.form.get('status')
    admin_response = request.form.get('admin_response')
    
    if status:
        feedback.status = status
    if admin_response is not None:
        feedback.admin_response = admin_response
    
    feedback.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Обратная связь обновлена', 'success')
    return redirect(url_for('feedback_detail', feedback_id=feedback_id))

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
@login_required
def feedback_delete(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    
    flash('Обратная связь удалена', 'success')
    return redirect(url_for('feedback_list'))

@app.route('/feedback/stats')
@login_required
def feedback_stats():
    # Получаем все записи и группируем в Python
    all_feedback = Feedback.query.all()
    
    # Статистика по типам обращений
    type_counts = {}
    for feedback in all_feedback:
        feedback_type = feedback.feedback_type.lower() if feedback.feedback_type else 'unknown'
        type_counts[feedback_type] = type_counts.get(feedback_type, 0) + 1
    
    type_stats = [{'type': t, 'count': c} for t, c in type_counts.items()]
    
    # Статистика по статусам
    status_counts = {}
    for feedback in all_feedback:
        status = feedback.status.lower() if feedback.status else 'unknown'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    status_stats = [{'status': s, 'count': c} for s, c in status_counts.items()]
    
    # Статистика по дням (последние 30 дней)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    daily_counts = {}
    for feedback in all_feedback:
        if feedback.created_at and feedback.created_at >= thirty_days_ago:
            date_str = feedback.created_at.strftime('%Y-%m-%d')
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
    
    daily_stats = [{'date': date, 'count': count} for date, count in sorted(daily_counts.items())]
    
    return jsonify({
        'type_stats': type_stats,
        'status_stats': status_stats,
        'daily_stats': daily_stats
    })

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

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    feedback_type = db.Column(db.String, nullable=False)  # bug, feature, general, other (или BUG, FEATURE, etc.)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String, default='new')  # new, in_progress, resolved, closed (или NEW, IN_PROGRESS, etc.)
    admin_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User')

# ===== Сонастройка (банк вопросов с вариантами) =====
class TuneQuestionType(str):
    TEXT = 'text'
    MCQ = 'mcq'


class TuneQuizQuestion(db.Model):
    __tablename__ = 'tune_quiz_questions'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=True)
    text = db.Column(db.Text)
    text_about_partner = db.Column(db.Text)
    text_about_self = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)
    question_type = db.Column(db.String, nullable=False, default='mcq')
    option1 = db.Column(db.String)
    option2 = db.Column(db.String)
    option3 = db.Column(db.String)
    option4 = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/tune/questions')
@login_required
def tune_questions():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', '')
    q = TuneQuizQuestion.query
    if category_filter:
        q = q.filter(TuneQuizQuestion.category.ilike(f"%{category_filter}%"))
    items = q.order_by(TuneQuizQuestion.number.nullslast(), TuneQuizQuestion.id).paginate(page=page, per_page=20, error_out=False)
    categories = db.session.query(TuneQuizQuestion.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('tune_questions.html', items=items, categories=categories, current_category=category_filter)


@app.route('/tune/questions/add', methods=['GET', 'POST'])
@login_required
def tune_add_question():
    if request.method == 'POST':
        number = request.form.get('number')
        text = request.form.get('text', '').strip()
        text_about_partner = request.form.get('text_about_partner', '').strip()
        text_about_self = request.form.get('text_about_self', '').strip()
        category = request.form.get('category', '').strip()
        qtype = request.form.get('question_type', 'mcq')
        option1 = request.form.get('option1', '').strip()
        option2 = request.form.get('option2', '').strip()
        option3 = request.form.get('option3', '').strip()
        option4 = request.form.get('option4', '').strip()

        if qtype == 'mcq' and (not option1 or not option2 or not option3 or not option4):
            flash('Для MCQ нужно заполнить 4 варианта', 'error')
            return render_template('tune_question_form.html', item=None, action='add')

        item = TuneQuizQuestion(
            number=int(number) if number else None,
            text=text,
            text_about_partner=text_about_partner or None,
            text_about_self=text_about_self or None,
            category=category,
            question_type=qtype,
            option1=option1 or None,
            option2=option2 or None,
            option3=option3 or None,
            option4=option4 or None,
        )
        db.session.add(item)
        db.session.commit()
        flash('Вопрос добавлен', 'success')
        return redirect(url_for('tune_questions'))

    return render_template('tune_question_form.html', item=None, action='add')


@app.route('/tune/questions/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def tune_edit_question(item_id):
    item = TuneQuizQuestion.query.get_or_404(item_id)
    if request.method == 'POST':
        number = request.form.get('number')
        item.number = int(number) if number else None
        item.text = request.form.get('text', '').strip() or None
        item.text_about_partner = request.form.get('text_about_partner', '').strip() or None
        item.text_about_self = request.form.get('text_about_self', '').strip() or None
        item.category = request.form.get('category', '').strip()
        qtype = request.form.get('question_type', 'mcq')
        item.question_type = qtype
        item.option1 = request.form.get('option1', '').strip() or None
        item.option2 = request.form.get('option2', '').strip() or None
        item.option3 = request.form.get('option3', '').strip() or None
        item.option4 = request.form.get('option4', '').strip() or None

        if item.question_type == 'mcq' and (not item.option1 or not item.option2 or not item.option3 or not item.option4):
            flash('Для MCQ нужно заполнить 4 варианта', 'error')
            return render_template('tune_question_form.html', item=item, action='edit')

        db.session.commit()
        flash('Вопрос обновлён', 'success')
        return redirect(url_for('tune_questions'))

    return render_template('tune_question_form.html', item=item, action='edit')


@app.route('/tune/questions/delete/<int:item_id>', methods=['POST'])
@login_required
def tune_delete_question(item_id):
    item = TuneQuizQuestion.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Вопрос удалён', 'success')
    return redirect(url_for('tune_questions'))


@app.route('/tune/questions/upload', methods=['GET', 'POST'])
@login_required
def tune_upload_questions():
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
                df = pd.read_excel(file)
                df.columns = df.columns.str.lower().str.strip()
                # Нормализация альтернативных заголовков
                rename_map = {}
                if '№' in df.columns and 'номер' not in df.columns:
                    rename_map['№'] = 'номер'
                if 'вопрос про партнера' in df.columns and 'вопрос про партнёра' not in df.columns:
                    rename_map['вопрос про партнера'] = 'вопрос про партнёра'
                if rename_map:
                    df.rename(columns=rename_map, inplace=True)

                required_columns = ['номер', 'вопрос про партнёра', 'вопрос про себя', 'тематика', 'вариант1', 'вариант2', 'вариант3', 'вариант4']
                missing = [c for c in required_columns if c not in df.columns]
                if missing:
                    flash(f"В файле отсутствуют колонки: {', '.join(missing)}", 'error')
                    return render_template('upload_tune_questions.html')

                # Очищаем существующие tune-вопросы
                TuneQuizQuestion.query.delete()

                added = 0
                for _, row in df.iterrows():
                    if pd.isna(row['вопрос про партнёра']) or pd.isna(row['вопрос про себя']) or pd.isna(row['тематика']):
                        continue
                    if any(pd.isna(row[col]) for col in ['вариант1','вариант2','вариант3','вариант4']):
                        continue

                    item = TuneQuizQuestion(
                        number=int(row['номер']) if ('номер' in df.columns and pd.notna(row['номер'])) else None,
                        text=None,
                        text_about_partner=str(row['вопрос про партнёра']).strip(),
                        text_about_self=str(row['вопрос про себя']).strip(),
                        category=str(row['тематика']).strip(),
                        question_type='mcq',
                        option1=str(row['вариант1']).strip(),
                        option2=str(row['вариант2']).strip(),
                        option3=str(row['вариант3']).strip(),
                        option4=str(row['вариант4']).strip(),
                    )
                    db.session.add(item)
                    added += 1

                db.session.commit()
                flash(f'Успешно загружено {added} вопросов Сонастройки', 'success')
                return redirect(url_for('tune_questions'))
            except Exception as e:
                flash(f'Ошибка при обработке файла: {str(e)}', 'error')
                return render_template('upload_tune_questions.html')
        else:
            flash('Пожалуйста, загрузите файл Excel (.xlsx или .xls)', 'error')

    return render_template('upload_tune_questions.html')

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
        Feedback.__table__.create(db.engine, checkfirst=True)
        TuneQuizQuestion.__table__.create(db.engine, checkfirst=True)

        # Обновление схемы для tune_quiz_questions — добавляем недостающие колонки (PostgreSQL)
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE IF EXISTS tune_quiz_questions ADD COLUMN IF NOT EXISTS text_about_partner TEXT"))
                conn.execute(db.text("ALTER TABLE IF EXISTS tune_quiz_questions ADD COLUMN IF NOT EXISTS text_about_self TEXT"))
                conn.execute(db.text("ALTER TABLE IF EXISTS tune_quiz_questions ALTER COLUMN text DROP NOT NULL"))
                conn.commit()
        except Exception as e:
            print(f"Ошибка обновления схемы tune_quiz_questions: {e}")
        
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
