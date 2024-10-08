import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def list_models():
    """
    Fetches the list of available models from the Ollama API.

    Returns:
        list: A list of model names available in the API. 
        If an error occurs, an empty list is returned.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        data = response.json()
        return [model['model'] for model in data['models']]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return []

def generate_response(model, prompt):
    """
    Sends a prompt to the specified model via the Ollama API and retrieves the response.

    Args:
        model (str): The name of the model to use for generating the response.
        prompt (str): The input prompt to send to the model.

    Returns:
        str: The response generated by the model. 
        If an error occurs or the response format is unexpected, None is returned.
    """
    try:
        print(f"Sending request to Ollama API: model={model}, prompt={prompt}")
        response = requests.post(OLLAMA_API_URL, json={
            "model": model,
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()  # Raise an error for bad status codes
        print(f"API response status code: {response.status_code}")
        print(f"API response content: {response.text}")

        data = response.json()
        if "response" in data:
            print(f"Model response: {data['response']}")
            return data["response"]
        else:
            print(f"Unexpected API response format: {data}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
        print(f"Response content: {response.content}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None
