from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    applications = db.relationship('Application', back_populates='user', cascade='all, delete-orphan')

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    website = db.Column(db.String(255))

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id', ondelete='RESTRICT'), nullable=False, index=True)
    position = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(30), nullable=False, default='sent')
    link = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', back_populates='applications')
    
    __table_args__ = (
        db.CheckConstraint("status IN ('sent', 'viewed', 'interview', 'offer', 'rejected')", name='ck_applications_status'),
    )

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_token'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Добавлена эта связь, чтобы работало token_record.user
    user = db.relationship('User')