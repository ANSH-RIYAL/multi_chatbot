# Multi-Chatbot Interface

A modern web application that allows users to interact with multiple AI language models simultaneously. The interface provides a unified chat experience where users can receive responses from different AI services and select their preferred response.

## Features

- **Multi-Model Support**: Interact with multiple AI models simultaneously
  - Gemini Pro (Free tier)
  - GPT-3.5 Turbo
  - Grok
- **Clean Interface**: Modern, responsive design with a split-view layout
  - Chat history on the left
  - AI responses on the right
- **Conversation History**: Maintains chat history with selected responses
- **Service Status**: Real-time display of available AI services
- **Easy to Use**: No setup required - start chatting immediately
- **Response Selection**: Choose your preferred response from multiple AI models

## Product Management Features

- **User Feedback System**:
  - Thumbs up/down feedback for each response
  - Feedback tracking and analytics
  - Real-time feedback metrics display

- **A/B Testing Framework**:
  - Response format variations
  - Performance tracking
  - User preference analysis

- **Cost Tracking & Analytics**:
  - API call tracking
  - Cost per service
  - Usage metrics

- **Performance Metrics**:
  - Total API calls
  - User feedback summary
  - Cost analysis
  - Service performance comparison

## Business Impact

- **User Engagement**:
  - Track user satisfaction through feedback
  - Monitor service preferences
  - Optimize response quality

- **Cost Optimization**:
  - Monitor API usage costs
  - Identify cost-effective services
  - Optimize resource allocation

- **Product Improvement**:
  - Data-driven decision making
  - Continuous service optimization
  - User preference analysis

## Setup

1. Clone the repository:
```bash
git clone https://github.com/ANSH-RIYAL/multi_chatbot.git
cd multi_chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
GROK_API_KEY=your_grok_api_key
```

4. Start the server:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

5. Open your browser and navigate to:
```
http://localhost:8000
```

## Project Structure

```
multi_chatbot/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── ai_services.py   # AI service integrations
│   ├── auth.py          # Authentication handling
│   └── oauth.py         # OAuth configuration
├── templates/
│   └── index.html       # Main application template
├── static/
│   └── script.js        # Frontend JavaScript
├── data/
│   └── conversation_history.json  # Chat history storage
├── requirements.txt     # Python dependencies
└── .env                # Environment variables
```

## API Endpoints

- `GET /`: Main application interface
- `POST /api/chat`: Send message to AI services
- `POST /api/select_response`: Save selected response to history
- `GET /api/history`: Retrieve conversation history

## Technologies Used

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI Services**: 
  - Google Gemini
  - OpenAI GPT
  - Grok
- **Authentication**: JWT
- **Data Storage**: JSON files

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API
- OpenAI API
- Grok API
- FastAPI framework
