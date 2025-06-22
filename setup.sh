#!/bin/bash

echo "🚀 Setting up AI Agent..."
echo "=========================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ Node.js, npm, Python 3, and pip3 are installed"

# Install dependencies
echo "📦 Installing dependencies..."
npm run install-all

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key"
    echo "   You can get one from: https://platform.openai.com/"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo "=================="
echo "To start the application:"
echo "  npm run dev"
echo ""
echo "Then open:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:3001"
echo ""
echo "Don't forget to add your OpenAI API key to the .env file!" 