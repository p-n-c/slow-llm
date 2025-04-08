## Local LLM server

### Setup Instructions

1. **Install required packages:**

   ```bash
   pip install flask flask-cors llm
   ```

2. **Configure the server:**

   - Open the `llm-api-server.py` file
   - Set `DEFAULT_MODEL_ID` to your local model ID
   - If your model requires an API key, set it appropriately

3. **Start the server:**

   ```bash
   python llm-api-server.py
   ```

4. **Open the web client:**
   - Open `llm-web-client.html` in your browser
   - The client will automatically connect to the API server running at http://127.0.0.1:5000

### API Endpoints

The server provides these endpoints:

- `GET /models` - List all available models
- `POST /prompt` - Send a single prompt
- `POST /conversation` - Start a new conversation
- `POST /conversation/<id>/prompt` - Send a prompt to an existing conversation
- `GET /conversation/<id>` - Get conversation history
- `DELETE /conversation/<id>` - Delete a conversation

### Features

- **Model Selection**: Choose from available local models
- **Single Prompt Mode**: Send one-off prompts with optional system instructions
- **Conversation Mode**: Maintain context across multiple interactions
- **Token Usage**: View input/output token counts when available
- **Simple Web Interface**: User-friendly design with clear visual feedback
