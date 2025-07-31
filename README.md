# Teacher AI Platform

A comprehensive AI-powered learning platform built with Flask that provides interactive chat, study material generation, and quiz functionality.

## Features

### 🤖 AI Chat Assistant
- Interactive chat interface similar to ChatGPT
- Create multiple chat sessions
- Save and retrieve chat history
- Real-time AI responses

### 📚 PDF Study Material Generator
- Generate comprehensive study materials on any topic
- Professional PDF formatting with images
- Includes introduction, key concepts, examples, and practice questions
- Easy download functionality

### 🧠 MCQ Quiz System
- AI-generated multiple choice questions
- Topic-based quiz creation
- Instant scoring and feedback
- Performance tracking and history
- Shareable results

### 👥 User Management
- Secure user registration and authentication
- User profiles and session management
- Quiz history and progress tracking

### 🔧 Admin Dashboard
- User management and analytics
- System statistics with charts
- User registration trends
- Quiz performance analytics
- Admin-only access controls

## Installation

1. **Clone the repository**
\`\`\`bash
git clone <repository-url>
cd teacher-ai-platform
\`\`\`

2. **Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. **Initialize the database**
\`\`\`bash
python scripts/setup_database.py
\`\`\`

4. **Run the application**
\`\`\`bash
python app.py
\`\`\`

5. **Access the application**
- Open your browser and go to `http://localhost:5000`
- Default admin credentials: username=`admin`, password=`admin123`

## Usage

### For Students
1. **Register** a new account or login
2. **Chat with AI** - Get instant help on any topic
3. **Generate PDFs** - Create study materials for your subjects
4. **Take Quizzes** - Test your knowledge with AI-generated questions
5. **Track Progress** - View your quiz history and performance

### For Administrators
1. **Login** with admin credentials
2. **View Dashboard** - Monitor system statistics
3. **Manage Users** - View and manage user accounts
4. **Analytics** - View detailed charts and performance data

## Database Schema

The application uses SQLite with the following tables:
- `users` - User accounts and authentication
- `chat_sessions` - Chat session management
- `chat_messages` - Individual chat messages and responses
- `quiz_sessions` - Quiz attempts and scores
- `quiz_questions` - Individual quiz questions and answers

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Charts**: Chart.js
- **PDF Generation**: ReportLab
- **Authentication**: Werkzeug security

## Configuration

### Environment Variables
- `SECRET_KEY` - Flask secret key for sessions
- `DATABASE_URL` - Database connection string (optional)

### AI Integration
Currently uses simulated AI responses. To integrate with real AI services:
1. Replace the AI response generation in `send_message()` route
2. Add API keys for services like OpenAI, Anthropic, etc.
3. Update the PDF generation to use AI for content creation

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Admin role-based access control
- SQL injection prevention with parameterized queries
- CSRF protection through Flask sessions

## Future Enhancements

- Real AI integration (OpenAI, Llama, etc.)
- Image generation for study materials
- Advanced quiz types (fill-in-the-blank, essay questions)
- Email notifications
- Mobile app support
- Multi-language support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
