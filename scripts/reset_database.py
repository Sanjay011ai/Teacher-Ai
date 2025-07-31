#!/usr/bin/env python3
"""
Reset database script for Teacher AI Platform
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def reset_database():
    """Reset the database to initial state"""
    print("🔄 Resetting Teacher AI database...")
    
    # Remove existing database
    if os.path.exists('teacher_ai.db'):
        os.remove('teacher_ai.db')
        print("✅ Removed existing database")
    
    # Create new database
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chat sessions table
    cursor.execute('''
        CREATE TABLE chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT UNIQUE NOT NULL,
            title TEXT DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Chat messages table
    cursor.execute('''
        CREATE TABLE chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_id INTEGER,
            message TEXT NOT NULL,
            response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Quiz sessions table
    cursor.execute('''
        CREATE TABLE quiz_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT NOT NULL,
            difficulty TEXT DEFAULT 'intermediate',
            total_questions INTEGER,
            correct_answers INTEGER,
            score REAL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Quiz questions table
    cursor.execute('''
        CREATE TABLE quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            user_answer TEXT,
            FOREIGN KEY (session_id) REFERENCES quiz_sessions (id)
        )
    ''')
    
    # AI Models table
    cursor.execute('''
        CREATE TABLE ai_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            size TEXT,
            is_available BOOLEAN DEFAULT TRUE,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ Created database tables")
    
    # Create default admin account
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin@teacherai.com', admin_password, True))
    print("✅ Created admin account: admin / admin123")
    
    # Create sample users
    sample_users = [
        ('john_doe', 'john@example.com', 'password123'),
        ('jane_smith', 'jane@example.com', 'password123'),
        ('student1', 'student1@example.com', 'password123'),
        ('teacher1', 'teacher1@example.com', 'password123')
    ]
    
    for username, email, password in sample_users:
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        print(f"✅ Created user: {username} / {password}")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Database reset complete!")
    print("\n📋 Available accounts:")
    print("   Admin: admin / admin123")
    print("   Users: john_doe, jane_smith, student1, teacher1 / password123")

if __name__ == "__main__":
    reset_database()
