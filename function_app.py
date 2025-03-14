import os
import azure.functions as func
import json
from openai import AzureOpenAI
from django.utils.html import escape

# OpenAI Configuration with Azure
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","3psXrHeuNTFLc8klzOkN9bhPX3mThjBnByzwMtfwFMc72GSLkzacJQQJ99BCACHYHv6XJ3w3AAAAACOGkBeY")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION","2024-05-01-preview")
OPENAI_AZURE_ENDPOINT = os.getenv("OPENAI_AZURE_ENDPOINT","https://manue-m89cvjpp-eastus2.openai.azure.com/openai/deployments/gpt-4o/chat/completions")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

openai = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION,
    azure_endpoint=OPENAI_AZURE_ENDPOINT
)

def ask_openai(history):
    """
    Sends conversation history to OpenAI and gets a response.
    """
    response = openai.chat.completions.create(
        messages=[{"role": "user", "content": [{"type": "text", "text": msg}]} for msg in history],
        model=OPENAI_MODEL,
        stream=False,
        max_tokens=4096,
        temperature=0,
        frequency_penalty=0.01
    )

    return response.choices[0].message.content.strip()

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function that receives conversation history and returns OpenAI's response.
    """
    try:
        req_body = req.get_json()
        history = req_body.get("history", [])

        if not history:
            return func.HttpResponse(json.dumps({"error": "No conversation history provided"}), 
                                     status_code=400, mimetype="application/json")

        # Escape messages to prevent XSS
        escaped_history = [escape(msg) for msg in history]

        # Call OpenAI
        response_text = ask_openai(escaped_history)

        return func.HttpResponse(json.dumps({"response": response_text}), mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")
