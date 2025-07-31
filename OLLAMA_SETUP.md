# Ollama Integration Setup Guide

This guide will help you set up Ollama integration with the Teacher AI Platform for local AI model support.

## 🚀 Quick Start

### 1. Install Ollama

**Windows/Mac/Linux:**
1. Visit [https://ollama.ai](https://ollama.ai)
2. Download and install Ollama for your operating system
3. Follow the installation instructions

**Alternative - Command Line:**
\`\`\`bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
\`\`\`

### 2. Start Ollama Service

\`\`\`bash
ollama serve
\`\`\`

Keep this terminal window open while using the Teacher AI Platform.

### 3. Install AI Models

**Recommended models:**

\`\`\`bash
# Fast and efficient (recommended for most users)
ollama pull llama3.2

# Very fast, smaller model
ollama pull llama3.2:1b

# Good for programming questions
ollama pull codellama

# Alternative general-purpose model
ollama pull mistral
\`\`\`

### 4. Run Setup Script

\`\`\`bash
python scripts/setup_ollama.py
\`\`\`

This script will:
- Check if Ollama is installed and running
- Install a default model if none are available
- Test the installation
- Provide troubleshooting guidance

## 🔧 Configuration

### Default Model
The platform uses `llama3.2` as the default model. You can change this in `app.py`:

```python
DEFAULT_MODEL = "llama3.2"  # Change to your preferred model
