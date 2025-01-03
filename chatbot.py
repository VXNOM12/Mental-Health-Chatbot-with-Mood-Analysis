import numpy as np
from transformers import pipeline
from textblob import TextBlob
import datetime
import json
import re
from flask import Flask, request, jsonify
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

class EmotionRecognizer:
    def __init__(self):
        self.emotion_classifier = pipeline("text-classification", 
                                        model="j-hartmann/emotion-english-distilroberta-base", 
                                        return_all_scores=True)
        
        self.emotion_indicators = {
            'joy': ['happy', 'excited', 'delighted', 'grateful', 'blessed'],
            'sadness': ['sad', 'depressed', 'down', 'unhappy', 'miserable'],
            'anger': ['angry', 'furious', 'irritated', 'frustrated', 'mad'],
            'fear': ['scared', 'anxious', 'worried', 'nervous', 'terrified'],
            'surprise': ['shocked', 'surprised', 'amazed', 'astonished'],
            'love': ['love', 'caring', 'affection', 'fond', 'attached'],
        }
    
    def analyze(self, text):
        # Get emotion scores from model
        emotions = self.emotion_classifier(text)[0]
        
        # Get dominant emotion
        dominant_emotion = max(emotions, key=lambda x: x['score'])
        
        # Count emotion keywords
        word_emotions = self._count_emotion_words(text.lower())
        
        return {
            'dominant_emotion': dominant_emotion['label'],
            'confidence': dominant_emotion['score'],
            'all_emotions': emotions,
            'emotion_keywords': word_emotions
        }
    
    def _count_emotion_words(self, text):
        words = word_tokenize(text)
        emotion_counts = {}
        
        for emotion, indicators in self.emotion_indicators.items():
            count = sum(1 for word in words if word in indicators)
            if count > 0:
                emotion_counts[emotion] = count
                
        return emotion_counts

class MentalHealthChatbot:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.emotion_recognizer = EmotionRecognizer()
        
        # Load customizable responses
        self.load_responses('responses.json')
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Initialize user profile
        self.user_profile = {
            'name': None,
            'preferred_topics': [],
            'triggers': [],
            'coping_strategies': []
        }
    
    def load_responses(self, filename='responses.json'):
        try:
            with open(filename, 'r') as f:
                self.responses = json.load(f)
        except FileNotFoundError:
            # Default responses if file not found
            self.responses = {
                "emotions": {
                    "joy": [
                        "I'm happy to hear you're feeling good! What's bringing you joy?",
                        "That's wonderful! Would you like to share more about these positive feelings?"
                    ],
                    "sadness": [
                        "I hear that you're feeling sad. Would you like to talk about it?",
                        "It's okay to feel sad sometimes. What do you think triggered these feelings?"
                    ],
                    "anger": [
                        "I can sense that you're angry. Would you like to explore what's causing this?",
                        "Your anger is valid. Let's talk about what's frustrating you."
                    ],
                    "fear": [
                        "It sounds like you're feeling anxious. What's making you worried?",
                        "I understand that you're scared. Would you like to talk about your fears?"
                    ],
                    "surprise": [
                        "That does sound surprising! How are you processing this?",
                        "Unexpected things can be overwhelming. Would you like to talk about it?"
                    ],
                    "love": [
                        "It's beautiful to hear about these feelings of love and connection.",
                        "Those are wonderful feelings to have. Would you like to share more?"
                    ]
                },
                "greetings": [
                    "Hello! How are you feeling today?",
                    "Hi there! Would you like to talk about how you're doing?",
                    "Welcome back! How has your day been?"
                ],
                "crisis": [
                    "I hear that you're going through a really tough time. Please know that help is available. The Crisis Helpline (988) has caring people ready to listen 24/7.",
                    "I understand you're in pain. Would you like to talk to a professional? The Crisis Helpline (988) is available anytime."
                ],
                "coping_suggestions": {
                    "sadness": [
                        "Would you like to try some deep breathing exercises?",
                        "Sometimes going for a walk can help clear your mind.",
                        "Would you like to talk about things that usually cheer you up?"
                    ],
                    "anger": [
                        "Let's try counting to ten together.",
                        "Would you like to try some progressive muscle relaxation?",
                        "Sometimes writing down our feelings can help process them."
                    ],
                    "fear": [
                        "Let's focus on grounding exercises. Can you name 5 things you can see?",
                        "Would you like to try some calming breathing exercises?",
                        "Remember that this feeling will pass. You're safe right now."
                    ]
                }
            }
    
    def update_responses(self, new_responses):
        """Update response templates"""
        self.responses.update(new_responses)
    
    def generate_response(self, user_input):
        """Generate response based on emotional analysis and user profile"""
        # Analyze emotion and sentiment
        emotion_analysis = self.emotion_recognizer.analyze(user_input)
        mood_analysis = self.analyze_mood(user_input)
        
        # Check for crisis keywords
        is_crisis = self.detect_crisis_keywords(user_input)
        
        # Generate appropriate response
        if is_crisis:
            response = np.random.choice(self.responses["crisis"])
        else:
            # Get emotion-specific response
            emotion = emotion_analysis['dominant_emotion']
            if emotion in self.responses["emotions"]:
                response = np.random.choice(self.responses["emotions"][emotion])
                
                # Add coping suggestion if negative emotion
                if emotion in ['sadness', 'anger', 'fear'] and "coping_suggestions" in self.responses:
                    response += "\n\n" + np.random.choice(self.responses["coping_suggestions"][emotion])
            else:
                # Fallback to sentiment-based response
                if mood_analysis['sentiment'] == 'POSITIVE':
                    response = np.random.choice(self.responses["emotions"]["joy"])
                else:
                    response = np.random.choice(self.responses["emotions"]["sadness"])
        
        # Store interaction
        self.conversation_history.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'user_input': user_input,
            'emotion_analysis': emotion_analysis,
            'mood_analysis': mood_analysis,
            'response': response,
            'is_crisis': is_crisis
        })
        
        return {
            'response': response,
            'emotion_analysis': emotion_analysis,
            'mood_analysis': mood_analysis,
            'is_crisis': is_crisis
        }
    
    # ... (previous methods remain the same)

# Flask API implementation
app = Flask(__name__)
chatbot = MentalHealthChatbot()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data['message']
        response = chatbot.generate_response(user_input)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/update_responses', methods=['POST'])
def update_responses():
    try:
        data = request.get_json()
        chatbot.update_responses(data)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/profile', methods=['POST'])
def main():
    """Run chatbot in console mode"""
    print("Mental Health Chatbot initialized. Type 'quit' to exit.")
    print("Bot: " + np.random.choice(chatbot.responses["greetings"]))
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            chatbot.save_conversation()
            break
            
        response = chatbot.generate_response(user_input)
        print("\nBot:", response['response'])
        
        if response['is_crisis']:
            print("\nCRISIS RESOURCES:")
            print("National Crisis Hotline: 988")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--api':
        app.run(debug=True)
    else:
        main()