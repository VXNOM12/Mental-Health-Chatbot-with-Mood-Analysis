# Mental Health Chatbot with Emotion Recognition

A Python-based chatbot that provides mental health support through emotional recognition and personalized responses.

## Features

- Real-time emotion analysis using transformer models
- Sentiment analysis and mood detection
- Crisis keyword detection and support resources
- Customizable responses through JSON configuration
- Conversation history tracking
- User profile management
- RESTful API endpoints

## Prerequisites

- Python 3.7+
- pip package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/VXNOM12/Mental-Health-Chatbot-with-Mood-Analysis.git
cd Mental-Health-Chatbot-with-Mood-Analysis

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Create `responses.json` for custom responses (optional)
2. Adjust emotion indicators in `EmotionRecognizer` class
3. Modify crisis keywords as needed

## Usage

### Console Mode
```bash
python chatbot.py
```

### API Mode
```bash
python chatbot.py --api
```

## API Endpoints

- POST `/chat`: Send messages to chatbot
- POST `/update_responses`: Update response templates
- POST `/profile`: Update user profile
- GET `/history`: Retrieve conversation history

## Example API Requests

```python
# Chat endpoint
POST /chat
{
    "message": "I'm feeling really happy today!"
}

# Update profile
POST /profile
{
    "name": "John",
    "preferred_topics": ["anxiety", "stress"],
    "coping_strategies": ["breathing", "meditation"]
}
```

## Safety Features

- Crisis detection and helpline information
- Professional help recommendations
- Non-therapeutic disclaimer
- Privacy considerations


## Disclaimer

This chatbot is not a replacement for professional mental health services. In case of emergency, contact your local crisis hotline or mental health professional.
