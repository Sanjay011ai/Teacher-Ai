#!/usr/bin/env python3
"""
Simple setup script for role-based Teacher AI Platform
"""

import sqlite3
import os

def setup_simple_database():
    """Setup simplified database without passwords"""
    print("🚀 Setting up simplified Teacher AI database...")
    
    # Remove existing database
    if os.path.exists('teacher_ai.db'):
        os.remove('teacher_ai.db')
        print("✅ Removed existing database")
    
    # Create new database
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    
    # Users table - no password required
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
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
    
    print("✅ Created database tables")
    
    # Create some sample users for testing
    sample_users = [
        ('demo_student', 'student@demo.com', 'student'),
        ('demo_teacher', 'teacher@demo.com', 'teacher'),
        ('demo_admin', 'admin@demo.com', 'admin')
    ]
    
    for username, email, role in sample_users:
        cursor.execute('''
            INSERT INTO users (username, email, role)
            VALUES (?, ?, ?)
        ''', (username, email, role))
        print(f"✅ Created demo user: {username} ({role})")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Simple database setup complete!")
    print("\n📋 How to use:")
    print("1. Go to the login page")
    print("2. Select your role (Student, Teacher, or Admin)")
    print("3. Click 'Enter Platform' - no password needed!")
    print("4. Or use the 'Register' page to create a new profile")

if __name__ == "__main__":
    setup_simple_database()
