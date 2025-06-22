# AI Agent - ChatGPT-like Chat Assistant

A modern, full-stack AI chat application built with React frontend and Python FastAPI backend, powered by OpenAI's GPT API. Features a beautiful, responsive UI with real-time messaging capabilities.

## ✨ Features

- 🤖 **AI-Powered Conversations**: Powered by OpenAI's GPT-3.5-turbo model
- 💬 **Real-time Chat**: Live messaging with WebSocket connections
- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations
- 📱 **Mobile Responsive**: Works perfectly on all devices
- ⚡ **Real-time Typing Indicators**: See when the AI is responding
- 🔄 **Conversation History**: Maintains context throughout the session
- 🎯 **Connection Status**: Visual indicator of server connection
- 🐍 **Python Backend**: Fast, modern FastAPI with async support

## 🚀 Quick Start

### Prerequisites

- Node.js (v14 or higher)
- Python 3.8 or higher
- npm or yarn
- pip3
- OpenAI API key

### Installation

1. **Clone and install dependencies:**
   ```bash
   npm run install-all
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your-openai-api-key-here
   PORT=3001
   ```

3. **Get your OpenAI API key:**
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Create an account and get your API key
   - Replace `your-openai-api-key-here` in the `.env` file

4. **Start the application:**
   ```bash
   npm run dev
   ```

5. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:3001

## 📁 Project Structure

```
ai-agent/
├── client/                 # React frontend
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Beautiful styling
│   │   └── index.js       # React entry point
│   └── package.json
├── server/
│   └── main.py            # FastAPI + WebSocket server
├── requirements.txt       # Python dependencies
├── package.json           # Root dependencies
├── setup.sh              # Automated setup script
├── README.md             # Comprehensive documentation
└── .gitignore           # Git ignore rules
```

## 🛠️ Available Scripts

- `npm run dev` - Start both frontend and backend in development mode
- `npm run server` - Start only the Python backend
- `npm run server:dev` - Start Python backend with auto-reload
- `npm run client` - Start only the React frontend
- `npm run build` - Build the React app for production
- `npm run install-all` - Install dependencies for frontend, backend, and Python

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `PORT` | Server port | 3001 |

### Customization

You can customize the AI behavior by modifying the system prompt in `server/main.py`:

```python
{
    "role": "system",
    "content": "You are a helpful AI assistant. Be concise, friendly, and helpful in your responses."
}
```

## 🎨 UI Features

- **Gradient Background**: Beautiful purple-blue gradient
- **Glass Morphism**: Modern frosted glass effect
- **Smooth Animations**: Fade-in effects and hover states
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme**: Automatic theme adaptation
- **Typing Indicators**: Real-time feedback when AI is responding

## 🔌 API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/chat` - REST API for chat
- `WebSocket /ws` - Real-time WebSocket connection for live chat

## 🚀 Deployment

### Frontend (React)
```bash
npm run build
# Deploy the build folder to your hosting service
```

### Backend (Python FastAPI)
```bash
# Deploy to services like:
# - Heroku
# - Railway
# - DigitalOcean App Platform
# - AWS Lambda
# - Google Cloud Run
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- FastAPI for the excellent Python web framework
- React team for the amazing framework
- Lucide React for beautiful icons

## 🆘 Support

If you encounter any issues:

1. Check that your OpenAI API key is valid
2. Ensure all dependencies are installed (both Node.js and Python)
3. Verify the server is running on port 3001
4. Check the browser console for any errors

---

**Happy chatting! 🤖💬** 