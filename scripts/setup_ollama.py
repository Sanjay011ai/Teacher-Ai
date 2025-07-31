#!/usr/bin/env python3
"""
Setup script for Ollama integration with Teacher AI Platform
"""

import requests
import json
import time
import subprocess
import sys
import os

OLLAMA_BASE_URL = "http://localhost:11434"
RECOMMENDED_MODELS = [
    "llama3.2",      # Fast and efficient for general tasks
    "llama3.2:1b",   # Very fast, good for quick responses
    "codellama",     # Good for programming-related questions
    "mistral",       # Alternative general-purpose model
    "phi3",          # Microsoft's efficient model
]

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_ollama_service():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")
    try:
        # Try to start Ollama in the background
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for service to start
        for i in range(10):
            if check_ollama_running():
                print("✅ Ollama service started successfully!")
                return True
            time.sleep(2)
            print(f"   Waiting for service to start... ({i+1}/10)")
        
        return False
    except Exception as e:
        print(f"❌ Failed to start Ollama service: {e}")
        return False

def list_installed_models():
    """List currently installed models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
    except:
        pass
    return []

def pull_model(model_name):
    """Pull/download a model"""
    print(f"📥 Downloading model: {model_name}")
    print("   This may take several minutes depending on model size...")
    
    try:
        # Use subprocess to run ollama pull command
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully downloaded {model_name}")
            return True
        else:
            print(f"❌ Failed to download {model_name}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False

def test_model(model_name):
    """Test if a model is working"""
    print(f"🧪 Testing model: {model_name}")
    
    try:
        payload = {
            "model": model_name,
            "prompt": "Hello! Can you help me learn?",
            "stream": False
        }
        
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'response' in result:
                print(f"✅ {model_name} is working correctly!")
                print(f"   Sample response: {result['response'][:100]}...")
                return True
        
        print(f"❌ {model_name} test failed")
        return False
        
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        return False

def main():
    print("🎓 Teacher AI Platform - Ollama Setup")
    print("=" * 50)
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("❌ Ollama is not installed!")
        print("\n📋 Installation Instructions:")
        print("1. Visit: https://ollama.ai")
        print("2. Download and install Ollama for your operating system")
        print("3. Run this setup script again")
        return False
    
    print("✅ Ollama is installed")
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("⚠️  Ollama service is not running")
        
        # Try to start the service
        if not start_ollama_service():
            print("\n❌ Could not start Ollama service automatically")
            print("\n📋 Manual start instructions:")
            print("1. Open a terminal/command prompt")
            print("2. Run: ollama serve")
            print("3. Keep that terminal open")
            print("4. Run this setup script again")
            return False
    else:
        print("✅ Ollama service is running")
    
    # List currently installed models
    installed_models = list_installed_models()
    print(f"\n📚 Currently installed models: {len(installed_models)}")
    for model in installed_models:
        print(f"   - {model}")
    
    # Check if we have at least one recommended model
    has_recommended = any(model.startswith(rec.split(':')[0]) 
                         for model in installed_models 
                         for rec in RECOMMENDED_MODELS)
    
    if not has_recommended:
        print(f"\n🔄 No recommended models found. Installing {RECOMMENDED_MODELS[0]}...")
        if pull_model(RECOMMENDED_MODELS[0]):
            installed_models.append(RECOMMENDED_MODELS[0])
        else:
            print("❌ Failed to install default model")
            return False
    
    # Test the first available model
    if installed_models:
        test_model(installed_models[0])
    
    print("\n🎉 Ollama setup complete!")
    print("\n📋 Next steps:")
    print("1. Start the Teacher AI Platform: python app.py")
    print("2. The platform will automatically use Ollama for AI features")
    print("3. You can install additional models using: ollama pull <model_name>")
    
    print(f"\n🔧 Recommended models for different use cases:")
    print("   - llama3.2:1b    (Fastest, good for quick responses)")
    print("   - llama3.2       (Balanced speed and quality)")
    print("   - codellama      (Best for programming questions)")
    print("   - mistral        (Alternative general-purpose)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
