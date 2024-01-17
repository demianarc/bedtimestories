from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# GPT-3 client setup
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Function to generate story with GPT-3.5 Turbo
def generate_story_with_gpt(theme, hero_name, story_length, value):
    try:
        # Token limits based on story length to avoid cutting off
        token_limits = {
            'Very Short': 150,
            'Short': 300,
            'Medium': 600,
            'Long': 1024
        }
        
        # Constructing the prompt
        prompt_intro = f"Write a beautiful children's story about a hero named {hero_name}. Use creative writing techniques. "
        prompt_body = f"who embodies and exemplifies the value of {value} in a {theme} setting. "
        prompt_conclusion = f"The story should be {story_length}, heartwarming and conclude with a moral lesson.It should be nicely formatted, with bold and line jumps when necessary. Don't overstate the hero's name."
        promptend = f"Format the story with an introductory sentence, followed by paragraphs, and end with a concluding sentence that includes a moral of the story, but in a creative way. "
        prompt = prompt_intro + prompt_body + prompt_conclusion + promptend

    

        # Making the API call using the correct format
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled and imaginative storyteller, used to avoiding repetitions."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extracting and returning the story text
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Handling exceptions
        print(f"An error occurred: {e}")
        return "An error occurred while generating the story. Please try again later."

# Route to serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle story generation
@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.json
    theme = data.get('theme')
    hero_name = data.get('heroName')
    story_length = data.get('storyLength')
    value = data.get('values')

    story = generate_story_with_gpt(theme, hero_name, story_length, value)
    return jsonify({"story": story})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
