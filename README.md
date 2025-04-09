## Local LLM server

### Setup Instructions

1. **Install required packages:**

   ```bash
   pip install flask flask-cors llm
   ```

2. **Configure the model:**
   By default, the server uses the `Llama-3` model from [gpt4all](https://github.com/nomic-ai/gpt4all) with a maximum output of 750 tokens. To change this, update environment variables before starting the server.

   ```bash
   # On bash
   export DEFAULT_MODEL_ID="your-prefered-model"
   export MAX_TOKENS=42
   ```

3. **Start the server:**

   ```bash
   npm start
   ```

4. **Open the web client:**
   Go directly to http://127.0.0.1:5000/client for a simple one-prompt interface.

   For more explanation, open the home page of the API server at http://127.0.0.1:5000.

### Remarks

- When using a local model for the first time, it will automatically download. You can follow the progress in the server output.
- You can control the LLM utility (e.g. add API Keys, install new models) from the CLI. Check the [manual](https://llm.datasette.io/) for all available commands or use `llm --help`.
- In particular, you will need to install the gpt4all local models plugin to run the server with the default `Llama-3` model.

  ```bash
  # Install the plugin
  llm install llm-gpt4all
  # List only the gpt4all models
  llm models | grep gpt4all
  ```

- Remember to restart the server if you change the environment variables.

### API Endpoints

The server provides these endpoints:

- `GET /models` - List all available models
- `POST /prompt` - Send a single prompt
- `POST /conversation` - Start a new conversation
- `POST /conversation/<id>/prompt` - Send a prompt to an existing conversation
- `GET /conversation/<id>` - Get conversation history
- `DELETE /conversation/<id>` - Delete a conversation
