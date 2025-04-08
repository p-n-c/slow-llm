## Local LLM server

### Setup Instructions

1. **Install required packages:**

   ```bash
   pip install flask flask-cors llm
   ```

2. **Configure the default model if needed:**
   The server uses the `Llama-3` model by default. To choose another model, change the `DEFAULT_MODEL_ID` environment variable.

   ```bash
   # On bash
   export DEFAULT_MODEL_ID="your-prefered-model"
   ```

3. **Start the server:**

   ```bash
   npm start
   ```

4. **Open the web client:**
   Go directly to http://127.0.0.1:5000/client.

   For more explanation, open the home page of the API server at http://127.0.0.1:5000.

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
