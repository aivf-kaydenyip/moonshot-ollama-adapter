from flask import Flask, render_template, request, redirect, session
from datetime import datetime

import json
import ollama
import logging

# Remove existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging
logging.basicConfig(
    filename="flask_app.log",  # Log file path
    level=logging.DEBUG,   # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    filemode="a"  # Append mode (default)
)

app = Flask("moonshot-ollama-adapter")

@app.route('/test', methods=['POST','GET'])
def handle_post():
    # print("Time:", datetime.now())
    # print("Request method:", request.method)
    # print("Request Headers:", request.headers if request.headers else None)
    # print("Request data:", request.json if hasattr(request, "json") else None)

    model_input = request.json['inputs']
    mdoel_output = ollama.chat(
        model='llama3:8b', 
        messages=[{
            'role': 'user',
            'content': model_input,
            }])
    
    print("Model Input:", model_input)
    print("Model Output:", mdoel_output['message']['content'])
    print()

    return app.response_class(
        response=json.dumps([{'generated_text': mdoel_output['message']['content']}]),
        status=200,
        mimetype="application/json"
    )

 
if __name__ == '__main__':
    app.run(debug=True, port=3100)