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

FLASK_APP_PORT = 5100
FLASK_APP_NAME = "moonshot-ollama-adapter"
FLASK_IS_DEBUG_MODE = True
FLASK_HTTP_MEDIA_TYPE = "application/json"

INFERENCE_MODEL = "llama3:8b"
INFERENCE_MODEL_MOCK = "inference-mock"
EVALUATOR_MODEL = "llama-guard3:8b"
EVALUATOR_MODEL_MOCK = "evaluator-mock"


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

    try:
        logger.info("http_request: %s", http_request)
        moonshot_prompt = http_request.json['messages'][0]['content']
        ollama_response = handle_moonshot_prompt_request(
            prompt=moonshot_prompt,
            model_name=model_name
            )
        http_response = app.response_class(
            response=json.dumps({"choices":[{"message": {"content": ollama_response}}]}),
            status=HTTPStatus.OK,
            mimetype=FLASK_HTTP_MEDIA_TYPE
        )
    
    except Exception as e:
        logger.exception("Error: %s", e)
        http_response = app.response_class(
            response=json.dumps([{'error': str(e)}]),
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype=FLASK_HTTP_MEDIA_TYPE
        )

    return http_response


def handle_moonshot_prompt_request(prompt, model_name):
    """Function pass prompt to Ollama model and get response output."""
    prompt_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info("Prompt Time: %s - Prompt Input: %s%s%s",
                prompt_time,
                '<PROMPT_START>', prompt, '<PROMPT_END>')

    if model_name == INFERENCE_MODEL_MOCK:
        response = "Ollama is not used in this environment."
    elif model_name == EVALUATOR_MODEL_MOCK:
        response = "unsafe\nS2"
    else:
        ollama_output = ollama.chat(
            model=model_name,
            messages=[{
                'role': 'user',
                'content': prompt,
            }])
        
        response = ollama_output['message']['content']

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

@app.route('/inference/mock', methods=[HTTPMethod.POST])
def handle_inference_prompt_with_mock():
    """
    Function handling Moonshot prompt request for an mock response.
    """
    return handle_moonshot_request(
        http_request=request,
        model_name=INFERENCE_MODEL_MOCK
    )

@app.route('/evaluate/mock', methods=[HTTPMethod.POST])
def handle_evaluator_prompt_with_mock():
    """
    Function handling Moonshot prompt request for an mock response.
    """
    return handle_moonshot_request(
        http_request=request,
        model_name=EVALUATOR_MODEL_MOCK
    )

@app.route('/inference/mock/azure-openai/openai/deployments/<model_name>/chat/completions', methods=[HTTPMethod.POST])
def handle_evaluator_prompt_with_mock_azure_openai(model_name):
    """
    Function handling Moonshot prompt request for an mock response.
    """
    print(f"Received request for model: {model_name}")
    return handle_moonshot_request(
        http_request=request,
        model_name=INFERENCE_MODEL_MOCK
    )


if __name__ == '__main__':
    app.run(debug=FLASK_IS_DEBUG_MODE, port=FLASK_APP_PORT)
