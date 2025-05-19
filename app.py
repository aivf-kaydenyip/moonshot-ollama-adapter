"""
Flask app to serve as an adapter for Moonshot's HuggingFace Connector
to access Ollama models.
"""
from logging.handlers import TimedRotatingFileHandler
from http import HTTPStatus, HTTPMethod
from datetime import datetime
import logging
import json

from flask import Flask, request, Response
import ollama


# Application constants/configurations
LOG_FILE_PATH = "logs/flask_app.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.DEBUG

FLASK_APP_PORT = 3100
FLASK_APP_NAME = "moonshot-ollama-adapter"
FLASK_IS_DEBUG_MODE = True
FLASK_HTTP_MEDIA_TYPE = "application/json"

INFERENCE_MODEL = "llama3:8b"
EVALUATOR_MODEL = "llama-guard3:8b"


# Module methods
def get_custom_logger(file_name, level, log_format) -> logging.Logger:
    """Return a file rolling logger."""
    # Rotate the log every midnight, keep 30 days of logs
    handler = TimedRotatingFileHandler(
        LOG_FILE_PATH, when="midnight", interval=1, backupCount=30
    )
    handler.setFormatter(logging.Formatter(log_format))

    cust_logger = logging.getLogger(file_name)
    cust_logger.setLevel(level)
    cust_logger.addHandler(handler)

    return cust_logger


def handle_moonshot_request(http_request, model_name) -> Response:
    """Function handling POST requests to /inference endpoint."""
    moonshot_prompt = http_request.json['inputs']
    ollama_response = handle_moonshot_prompt_request(
        prompt=moonshot_prompt,
        model_name=model_name
        )
    http_response = app.response_class(
        response=json.dumps([{'generated_text': ollama_response}]),
        status=HTTPStatus.OK,
        mimetype=FLASK_HTTP_MEDIA_TYPE
    )

    return http_response


def handle_moonshot_prompt_request(prompt, model_name):
    """Function pass prompt to Ollama model and get response output."""

    prompt_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info("Prompt Time: %s - Prompt Input: %s%s%s",
                prompt_time,
                '<PROMPT_START>', prompt, '<PROMPT_END>')

    model_output = ollama.chat(
        model=model_name,
        messages=[{
            'role': 'user',
            'content': prompt,
        }])

    response = model_output['message']['content']

    logger.info("Prompt Time: %s - Model Response: %s%s%s",
                prompt_time,
                '<RESPONSE_START>', response, "<REPONSE_END>")

    return response


logger = get_custom_logger(file_name=LOG_FILE_PATH, level=LOG_LEVEL,
                           log_format=LOG_FORMAT)
app = Flask(FLASK_APP_NAME)


@app.route('/inference', methods=[HTTPMethod.POST])
def handle_inference_prompt():
    """
    Function handling Moonshot prompt request for an Ollama inference endpoint.
    """
    return handle_moonshot_request(
        http_request=request,
        model_name=INFERENCE_MODEL
    )


@app.route('/evaluate', methods=[HTTPMethod.POST])
def handle_evaluator_prompt():
    """
    Function handling Moonshot prompt request for an Ollama evaluator endpoint.
    """
    return handle_moonshot_request(
        http_request=request,
        model_name=EVALUATOR_MODEL
    )


if __name__ == '__main__':
    app.run(debug=FLASK_IS_DEBUG_MODE, port=FLASK_APP_PORT)
