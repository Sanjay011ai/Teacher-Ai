from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from datetime import datetime
import sqlite3
import os
import json
from functools import wraps
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import base64
import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"

class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def is_available(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[Dict]:
        """Get list of available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
        except:
            pass
        return []
    
    def generate_response(self, prompt: str, model: str = DEFAULT_MODEL, system_prompt: str = None) -> str:
        """Generate response using Ollama"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', 'Sorry, I could not generate a response.')
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Request timed out. The model might be processing a complex query."
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

# Initialize Ollama client
ollama_client = OllamaClient()

# AI Service Functions
def generate_chat_response(message: str, context: List[Dict] = None) -> str:
    """Generate AI chat response with context"""
    if not ollama_client.is_available():
        return "Ollama is not available. Please make sure Ollama is running on your system."
    
    # Build context from previous messages
    context_prompt = ""
    if context:
        context_prompt = "\n".join([
            f"User: {msg.get('message', '')}\nAssistant: {msg.get('response', '')}"
            for msg in context[-5:]  # Last 5 messages for context
        ])
        context_prompt += "\n\n"
    
    system_prompt = """You are a helpful AI teaching assistant. You provide clear, educational responses and help students learn various subjects. Be encouraging, patient, and provide examples when helpful. If asked about complex topics, break them down into understandable parts."""
    
    full_prompt = f"{context_prompt}User: {message}\nAssistant:"
    
    return ollama_client.generate_response(full_prompt, system_prompt=system_prompt)

def generate_quiz_questions(topic: str, difficulty: str = "intermediate", num_questions: int = 3) -> List[Dict]:
    """Generate MCQ questions using Ollama"""
    if not ollama_client.is_available():
        return [
            {
                "question": f"Sample question about {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": "A"
            }
        ]
    
    system_prompt = f"""You are an expert quiz generator. Create {num_questions} multiple choice questions about {topic} at {difficulty} level. 

Format your response as a JSON array with this exact structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": "A",
    "explanation": "Brief explanation of why this is correct"
  }}
]

Make sure:
- Questions are clear and educational
- Options are plausible but only one is correct
- Difficulty matches the requested level
- Include brief explanations
- Return valid JSON only"""
    
    prompt = f"Generate {num_questions} {difficulty} level multiple choice questions about: {topic}"
    
    response = ollama_client.generate_response(prompt, system_prompt=system_prompt)
    
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            questions_data = json.loads(json_match.group())
            return questions_data
    except:
        pass
    
    # Fallback if JSON parsing fails
    return [
        {
            "question": f"What is an important concept to understand about {topic}?",
            "options": [
                "It requires foundational knowledge",
                "It can be learned quickly",
                "It has no practical applications",
                "It is only theoretical"
            ],
            "correct": "A",
            "explanation": "Understanding foundational concepts is crucial for mastering any topic."
        }
    ]

def generate_pdf_content(topic: str) -> Dict[str, str]:
    """Generate comprehensive PDF content using Ollama"""
    if not ollama_client.is_available():
        return {
            "introduction": f"This study material covers {topic}.",
            "key_concepts": f"Key concepts related to {topic}.",
            "examples": f"Practical examples of {topic}.",
            "practice_questions": f"Practice questions about {topic}.",
            "summary": f"Summary of {topic} concepts."
        }
    
    system_prompt = """You are an expert educational content creator. Generate comprehensive study material that is well-structured, informative, and educational. Use clear language and provide practical examples."""
    
    sections = {}
    
    # Generate each section
    section_prompts = {
        "introduction": f"Write a comprehensive introduction to {topic}. Explain what it is, why it's important, and what students will learn. Make it engaging and informative (200-300 words).",
        "key_concepts": f"List and explain the key concepts, principles, or components of {topic}. Use bullet points or numbered lists for clarity. Include definitions and brief explanations (300-400 words).",
        "examples": f"Provide 3-4 practical, real-world examples that illustrate {topic}. Make them relatable and easy to understand. Show how the concepts apply in practice (250-350 words).",
        "practice_questions": f"Create 5-7 practice questions about {topic} with brief answers. Include a mix of question types: multiple choice, short answer, and application questions (200-300 words).",
        "summary": f"Write a concise summary of {topic} that reinforces the main points. Include key takeaways and suggestions for further learning (150-200 words)."
    }
    
    for section, prompt in section_prompts.items():
        try:
            content = ollama_client.generate_response(prompt, system_prompt=system_prompt)
            sections[section] = content
        except:
            sections[section] = f"Content for {section} could not be generated at this time."
    
    return sections

# Database initialization
def init_db():
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    
    # Users table - simplified, no password
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chat sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
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
        CREATE TABLE IF NOT EXISTS chat_messages (
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
        CREATE TABLE IF NOT EXISTS quiz_sessions (
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
        CREATE TABLE IF NOT EXISTS quiz_questions (
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
    
    conn.commit()
    conn.close()
    print("✅ Database setup completed successfully!")

# Authentication decorator - simplified
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role', '').strip()
        
        if not role or role not in ['student', 'teacher', 'admin']:
            flash('Please select a valid role', 'error')
            return render_template('login.html')
        
        # Generate a simple session based on role
        session['user_id'] = f"{role}_user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        session['username'] = f"{role.title()} User"
        session['role'] = role
        session['email'] = f"{role}@teacherai.com"
        
        flash(f'Welcome! You are now logged in as {role.title()}', 'success')
        
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', '').strip()
        
        # Basic validation
        if not username or not email or not role:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if role not in ['student', 'teacher']:
            flash('Please select a valid role', 'error')
            return render_template('register.html')
        
        try:
            conn = sqlite3.connect('teacher_ai.db')
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Username or email already exists', 'error')
                conn.close()
                return render_template('register.html')
            
            # Create new user
            cursor.execute('''
                INSERT INTO users (username, email, role)
                VALUES (?, ?, ?)
            ''', (username, email, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Auto-login the user
            session['user_id'] = user_id
            session['username'] = username
            session['role'] = role
            session['email'] = email
            
            flash(f'Account created successfully! Welcome to Teacher AI, {username}!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Check Ollama status
    ollama_status = ollama_client.is_available()
    available_models = ollama_client.list_models() if ollama_status else []
    
    return render_template('dashboard.html', 
                         ollama_status=ollama_status,
                         available_models=available_models)

@app.route('/chat')
@login_required
def chat():
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT session_id, title, created_at 
        FROM chat_sessions 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    chat_sessions = cursor.fetchall()
    conn.close()
    
    # Get available models
    available_models = ollama_client.list_models()
    
    return render_template('chat.html', 
                         chat_sessions=chat_sessions,
                         available_models=available_models,
                         ollama_status=ollama_client.is_available())

@app.route('/new_chat', methods=['POST'])
@login_required
def new_chat():
    session_id = str(uuid.uuid4())
    
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_sessions (user_id, session_id, title)
        VALUES (?, ?, ?)
    ''', (session['user_id'], session_id, 'New Chat'))
    conn.commit()
    conn.close()
    
    return jsonify({'session_id': session_id})

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    session_id = data['session_id']
    message = data['message']
    model = data.get('model', DEFAULT_MODEL)
    
    # Get chat context
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT message, response 
        FROM chat_messages 
        WHERE session_id = ? AND user_id = ?
        ORDER BY timestamp DESC
        LIMIT 5
    ''', (session_id, session['user_id']))
    context = [{'message': row[0], 'response': row[1]} for row in cursor.fetchall()]
    context.reverse()  # Reverse to get chronological order
    
    # Generate AI response
    ai_response = generate_chat_response(message, context)
    
    # Save message and response
    cursor.execute('''
        INSERT INTO chat_messages (session_id, user_id, message, response)
        VALUES (?, ?, ?, ?)
    ''', (session_id, session['user_id'], message, ai_response))
    
    # Update chat title if it's the first message
    cursor.execute('SELECT COUNT(*) FROM chat_messages WHERE session_id = ?', (session_id,))
    message_count = cursor.fetchone()[0]
    
    if message_count == 1:
        # Generate a title from the first message
        title = message[:50] + "..." if len(message) > 50 else message
        cursor.execute('''
            UPDATE chat_sessions SET title = ? WHERE session_id = ?
        ''', (title, session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'response': ai_response})

@app.route('/get_chat_history/<session_id>')
@login_required
def get_chat_history(session_id):
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT message, response, timestamp 
        FROM chat_messages 
        WHERE session_id = ? AND user_id = ?
        ORDER BY timestamp ASC
    ''', (session_id, session['user_id']))
    messages = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'message': msg[0],
        'response': msg[1],
        'timestamp': msg[2]
    } for msg in messages])

@app.route('/pdf_generator')
@login_required
def pdf_generator():
    return render_template('pdf_generator.html', 
                         ollama_status=ollama_client.is_available())

@app.route('/generate_pdf', methods=['POST'])
@login_required
def generate_pdf():
    topic = request.form['topic']
    
    # Generate content using Ollama
    content_sections = generate_pdf_content(topic)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph(f"Study Material: {topic}", title_style))
    story.append(Spacer(1, 20))
    
    # Add generated content sections
    section_titles = {
        'introduction': 'Introduction',
        'key_concepts': 'Key Concepts',
        'examples': 'Examples and Applications',
        'practice_questions': 'Practice Questions',
        'summary': 'Summary and Key Takeaways'
    }
    
    for section_key, section_title in section_titles.items():
        if section_key in content_sections:
            story.append(Paragraph(section_title, styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Split content into paragraphs
            content = content_sections[section_key]
            paragraphs = content.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 8))
            
            story.append(Spacer(1, 20))
    
    # Add footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor='gray'
    )
    story.append(Paragraph(f"Generated by Teacher AI Platform", footer_style))
    story.append(Paragraph(f"Topic: {topic} | Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{topic.replace(' ', '_')}_study_material.pdf",
        mimetype='application/pdf'
    )

@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html', 
                         ollama_status=ollama_client.is_available())

@app.route('/start_quiz', methods=['POST'])
@login_required
def start_quiz():
    topic = request.form['topic']
    difficulty = request.form.get('difficulty', 'intermediate')
    
    # Generate questions using Ollama
    questions = generate_quiz_questions(topic, difficulty, 5)
    
    # Save quiz session
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quiz_sessions (user_id, topic, difficulty, total_questions, correct_answers, score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], topic, difficulty, len(questions), 0, 0))
    
    quiz_session_id = cursor.lastrowid
    
    # Save questions
    for i, q in enumerate(questions):
        cursor.execute('''
            INSERT INTO quiz_questions (session_id, question, option_a, option_b, option_c, option_d, correct_answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (quiz_session_id, q['question'], q['options'][0], q['options'][1], 
              q['options'][2], q['options'][3], q['correct'], q.get('explanation', '')))
    
    conn.commit()
    conn.close()
    
    return render_template('take_quiz.html', 
                         questions=questions, 
                         quiz_id=quiz_session_id, 
                         topic=topic,
                         difficulty=difficulty)

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    quiz_id = request.form['quiz_id']
    answers = request.form.to_dict()
    
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    
    # Get questions with explanations
    cursor.execute('SELECT id, correct_answer, explanation FROM quiz_questions WHERE session_id = ?', (quiz_id,))
    questions = cursor.fetchall()
    
    correct_count = 0
    results = []
    
    for q_id, correct_answer, explanation in questions:
        user_answer = answers.get(f'question_{q_id}', '')
        cursor.execute('UPDATE quiz_questions SET user_answer = ? WHERE id = ?', (user_answer, q_id))
        
        is_correct = user_answer == correct_answer
        if is_correct:
            correct_count += 1
            
        results.append({
            'question_id': q_id,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': explanation
        })
    
    # Update quiz session
    total_questions = len(questions)
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    cursor.execute('''
        UPDATE quiz_sessions 
        SET correct_answers = ?, score = ?, completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (correct_count, score, quiz_id))
    
    conn.commit()
    conn.close()
    
    return render_template('quiz_result.html', 
                         correct=correct_count, 
                         total=total_questions, 
                         score=score,
                         results=results)

@app.route('/quiz_history')
@login_required
def quiz_history():
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT topic, difficulty, total_questions, correct_answers, score, completed_at
        FROM quiz_sessions
        WHERE user_id = ?
        ORDER BY completed_at DESC
    ''', (session['user_id'],))
    history = cursor.fetchall()
    conn.close()
    
    return render_template('quiz_history.html', history=history)

# Admin routes
@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM users WHERE role != "admin"')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM chat_sessions')
    total_chats = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM quiz_sessions')
    total_quizzes = cursor.fetchone()[0]
    
    # Get recent users
    cursor.execute('''
        SELECT username, email, created_at
        FROM users
        WHERE role != "admin"
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    recent_users = cursor.fetchall()
    
    conn.close()
    
    # Get Ollama status and models
    ollama_status = ollama_client.is_available()
    available_models = ollama_client.list_models() if ollama_status else []
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_chats=total_chats,
                         total_quizzes=total_quizzes,
                         recent_users=recent_users,
                         ollama_status=ollama_status,
                         available_models=available_models)

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, email, role, created_at
        FROM users
        WHERE role != "admin"
        ORDER BY created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    conn = sqlite3.connect('teacher_ai.db')
    cursor = conn.cursor()
    
    # Get user registration data by month
    cursor.execute('''
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM users
        WHERE role != "admin"
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    ''')
    user_data = cursor.fetchall()
    
    # Get quiz performance data
    cursor.execute('''
        SELECT topic, AVG(score) as avg_score, COUNT(*) as attempts
        FROM quiz_sessions
        GROUP BY topic
        ORDER BY attempts DESC
        LIMIT 10
    ''')
    quiz_data = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_analytics.html', 
                         user_data=user_data, 
                         quiz_data=quiz_data)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_db()
    
    # Check Ollama availability on startup
    if ollama_client.is_available():
        print("✅ Ollama is available and ready!")
        models = ollama_client.list_models()
        if models:
            print(f"📚 Available models: {', '.join([m['name'] for m in models])}")
        else:
            print("⚠️  No models found. Please install a model using: ollama pull llama3.2")
    else:
        print("❌ Ollama is not available. Please start Ollama service.")
        print("   Install: https://ollama.ai")
        print("   Start: ollama serve")
        print("   Install model: ollama pull llama3.2")
    
    app.run(debug=True)
