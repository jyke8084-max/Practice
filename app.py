import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from database import db
from models import User, PasswordResetToken
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

# Загружаем переменные из .env
load_dotenv()

app = Flask(__name__)

# Настройки из .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

TOKEN_TTL_MINUTES = 30

# МАРШРУТЫ
@app.route('/')
def index():
    return "<h1>Главная страница JobTracker</h1><p>Проект успешно настроен</p>"

@app.route('/health/')
def health():
    return jsonify(status="ok", service="JobTracker")

# ФУНКЦИИ ВОССТАНОВЛЕНИЯ ПАРОЛЯ 
def create_reset_token(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return None
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires
    )
    db.session.add(reset_token)
    db.session.commit()
    return raw_token

def verify_reset_token(raw_token):
    token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
    token_record = PasswordResetToken.query.filter_by(token_hash=token_hash).first()
    if not token_record:
        return None
    if token_record.expires_at < datetime.now(timezone.utc):
        return None
    if token_record.used_at is not None:
        return None
    return token_record.user

# --- ТЕСТОВЫЕ МАРШРУТЫ (для проверки) ---
@app.route('/test_reset')
def test_reset():
    test_email = "test@example.com"
    user = User.query.filter_by(email=test_email).first()
    if not user:
        user = User(email=test_email, password_hash="fake_hash", full_name="Тестовый Пользователь")
        db.session.add(user)
        db.session.commit()
        return "Пользователь создан! Перезагрузите страницу (F5), чтобы сгенерировать токен."
    
    token = create_reset_token(test_email)
    verified_user = verify_reset_token(token)
    
    if verified_user:
        return f"<h1>Механизм работает!</h1><p>Владелец токена: {verified_user.full_name}</p>"
    else:
        return "<h1>Ошибка проверки токена</h1>"

if __name__ == '__main__':
    app.run(debug=True)