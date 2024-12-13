# AI Chat Assistant

A simple command-line chat interface powered by OpenAI's GPT-4o model.

## Setup

1. Clone the repository: 
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   API_BASE_URL=http://localhost:8000  # Required for Function Calling Assistant
   ```

4. Run one of the assistants:
   ```bash
   # For basic chat assistant:
   python assistant.py

   # For service desk assistant with function calling:
   python function_calling_assistant.py
   ```

## Usage

Once the application is running, you can start chatting with the AI assistant. Type your messages and press Enter to send them. The assistant will respond to your queries.

To exit the application, type any of the following commands:
- 'quit'
- 'exit'
- 'bye'

## Features

- Interactive command-line interface
- Powered by OpenAI's GPT-4o model
- Maintains conversation history for context
- Simple and easy to use
- Two assistant types:
  - Basic Assistant: General conversation
  - Function Calling Assistant: Service desk operations with API integration

## Requirements

- Python 3.6 or higher
- OpenAI API key
- Required Python packages (see requirements.txt)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
