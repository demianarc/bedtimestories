from flask import Flask, request, jsonify, render_template
import requests
import openai
from dotenv import load_dotenv
import os

# Load API keys from .env file
load_dotenv()
google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

@app.route('/')

def index_page():
     # other logic if any
     return render_template('index.html', google_maps_key=google_maps_key)

def index():
    return render_template('index.html')

# Function to get reviews from Google Maps
def get_reviews(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,reviews&key={google_maps_key}"
    response = requests.get(url)
    reviews = response.json().get('result', {}).get('reviews', [])
    return reviews

# Function to process reviews with GPT
def process_with_gpt(reviews):
    openai.api_key = openai_key
    review_texts = ' '.join([review['text'] for review in reviews])
    prompt = f"Analyze and summarize these {review_texts} from google maps into an engaging, witty, and informative brief (try and keep it no-nonsense, brutally honest at the same time). Write an engaging and reasonably witty brief as if you're texting a friend. The summary should be balanced, covering both positive and negative aspects in a light and humorous way. Avoid focusing on specifics from individual reviews. Instead, provide a general impression that captures the overall sentiment. Use casual language and reasonable amout of emojis to make it fun. Keep it under 5 sentences. Conclude with a brief personal recommendation (go or not). Remember, it should sound like an honest and casual conversation between friends, not a formal review."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a creative, informal, and engaging friend offering a balanced summary of a place."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7  # Adjusting creativity level
        )
        return response.choices[0].message["content"].strip()
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "An error occurred while processing the reviews. Please try again later."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "An unexpected error occurred. Please try again later."

@app.route('/get-reviews', methods=['POST'])
def get_reviews_endpoint():
    data = request.json
    place_id = data['place_id']
    if not place_id:
        return jsonify({'error': 'Place ID is required'}), 400
    reviews = get_reviews(place_id)
    summary = process_with_gpt(reviews)
    return jsonify({'summary': summary})


if __name__ == '__main__':
    app.run(debug=True)