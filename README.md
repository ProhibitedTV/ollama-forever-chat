# Ollama Chat App

A simple chat application that uses two Ollama models to have a conversation with each other. The application features a GUI built with Tkinter and includes Text-to-Speech (TTS) functionality using `pyttsx3`.

## Features

- GUI for interaction
- Two Ollama models conversing with each other
- Text-to-Speech (TTS) for distinct voices for each model
- Splash screen on startup
- Context-aware responses by maintaining a conversation history
- Dropdown selection for available models

## Requirements

- Python 3.x
- `ollama`
- `pyttsx3`
- `requests`
- `tkinter` (usually comes with Python installations)
- `Pillow`

## Installation

### Download and Install Ollama

1. Visit the Ollama website to download the appropriate version for your operating system.
2. Follow the installation instructions provided on the website to set up Ollama on your machine.
3. Start the local Ollama server by running the following command in your terminal:

```sh
ollama serve
```

### Download and Install Python

1. Visit the [Python website](https://www.python.org/downloads/) to download the latest version of Python 3.x for your operating system.
2. Follow the installation instructions provided on the website. Ensure that you add Python to your system PATH during the installation.

### Set Up the Chat Application

1. Clone the repository:

```sh
git clone https://github.com/yourusername/OllamaChatApp.git
cd OllamaChatApp
```

2. Create and activate a virtual environment (optional but recommended):

```sh
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

3. Install the required packages:

```sh
pip install -r requirements.txt
```

## Usage

1. Ensure that the local Ollama server is running:

```sh
ollama serve
```

2. Run the application:

```sh
python main.py
```

## Project Structure

```
OllamaChatApp/
├── images/             # Directory for storing image assets (e.g., splash screen, model images)
├── main.py             # Initializes and starts the application
├── chat.py             # Manages the chat interface and TTS
├── ollama_api.py       # Handles interaction with the Ollama API
├── requirements.txt    # Lists the dependencies
└── README.md           # Project documentation
```

## Dependencies

- `ollama`: API for interacting with Ollama models
- `pyttsx3`: Text-to-Speech conversion library
- `requests`: HTTP library for making API requests
- `tkinter`: GUI library for Python (usually included with Python installations)
- `Pillow`: Python Imaging Library for handling images

## License

This project is licensed under the MIT License.