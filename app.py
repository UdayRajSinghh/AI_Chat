from flask import Flask, request, Response, stream_with_context
from groq import Groq
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Groq client
client = Groq(
    api_key="os.getenv('GROQ_API_KEY')"  # Store your API key in .env file
)

@app.route('/')
def serve_app():
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    def generate():
        try:
            data = request.get_json()
            
            # Create the chat completion with streaming
            stream = client.chat.completions.create(
                messages=data['messages'],
                model="llama-3.3-70b-versatile",
                stream=True
            )

            # Stream each chunk back to the client
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print(f"Error: {str(e)}")
            yield f"Error: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == "__main__":
    # Get port from environment variable for Render
    port = int(os.getenv('PORT', 5000))

    # Run the app
    app.run(host='0.0.0.0', port=port)
