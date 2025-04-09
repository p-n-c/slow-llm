from flask import Flask, request, jsonify
from pprint import pprint
import llm
import os

app = Flask(__name__)

# Configure the model to use - change this to your local model
DEFAULT_MODEL_ID = os.environ.get("DEFAULT_MODEL_ID", "Llama-3")
MAX_TOKENS = os.environ.get("MAX_TOKENS", 750)

# You can set this in environment or directly here if needed
# os.environ["MODEL_API_KEY"] = "your-api-key-if-needed"

# Store active conversations
conversations = {}


@app.route('/', methods=['GET'])
def welcome_page():
    """Serve a welcome page at the root address"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LLM API Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }
            .container {
                background-color: #f9f9f9;
                border-radius: 5px;
                padding: 20px;
                margin-top: 20px;
            }
            code {
                background-color: #f1f1f1;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: monospace;
            }
            ul {
                margin-top: 10px;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>LLM API Server</h1>
        <div class="container">
            <h2>Welcome to the Local LLM API Server</h2>
            <p>This server provides a REST API for interacting with local LLM models.</p>

            <h3>Available Endpoints:</h3>
            <ul>
                <li><code>GET /models</code> - List all available models</li>
                <li><code>POST /prompt</code> - Send a single prompt</li>
                <li><code>POST /conversation</code> - Start a new conversation</li>
                <li><code>POST /conversation/&lt;id&gt;/prompt</code> - Send a prompt to a conversation</li>
                <li><code>GET /conversation/&lt;id&gt;</code> - Get conversation history</li>
                <li><code>DELETE /conversation/&lt;id&gt;</code> - Delete a conversation</li>
            </ul>

            <h3>Web Client:</h3>
            <p>Use our <a href="/client">web client</a> to interact with the API through a friendly interface.</p>
        </div>
    </body>
    </html>
    """


@app.route('/client', methods=['GET'])
def serve_client():
    """Serve the web client HTML"""
    try:
        with open('src/index.html', 'r') as f:
            html_content = f.read()
            # Inject model information into the HTML
            html_content = html_content.replace('</body>', f'''
            <script>
                window.SERVER_CONFIG = {{
                    DEFAULT_MODEL_ID: "{DEFAULT_MODEL_ID}",
                    MAX_TOKENS: {MAX_TOKENS}
                }};
            </script>
            </body>''')
            return html_content
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Client file not found</h1>
            <p>The web client file (index.html) was not found on the server.</p>
            <p><a href="/">Return to home</a></p>
        </body>
        </html>
        """


@app.route('/styles.css', methods=['GET'])
def serve_styles():
    """Serve the CSS file"""
    try:
        with open('src/styles.css', 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        return "CSS file not found", 404


@app.route('/script.js', methods=['GET'])
def serve_script():
    """Serve the JavaScript file"""
    try:
        with open('src/script.js', 'r') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "JavaScript file not found", 404


@app.route('/models', methods=['GET'])
def list_models():
    """List all available models"""
    models = [model.model_id for model in llm.get_models()]
    return jsonify({"models": models})


@app.route('/prompt', methods=['POST'])
def single_prompt():
    """Handle a single prompt without conversation history"""
    data = request.json

    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400

    model_id = data.get('model_id', DEFAULT_MODEL_ID)
    system_prompt = data.get('system', None)

    try:
        model = llm.get_model(model_id)
        response = model.prompt(
            data['prompt'],
            system=system_prompt,
            max_tokens=MAX_TOKENS
        )

        result = {
            "text": response.text(),
            "model": model_id,
            "usage": {
                "input_tokens": response.usage().input,
                "output_tokens": response.usage().output
            }}

        return jsonify(result)

    except llm.UnknownModelError:
        return jsonify({"error": f"Unknown model: {model_id}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/conversation', methods=['POST'])
def start_conversation():
    """Start a new conversation and return a conversation ID"""
    data = request.json
    model_id = data.get('model_id', DEFAULT_MODEL_ID)

    try:
        model = llm.get_model(model_id)
        conversation = model.conversation()

        # Generate a simple conversation ID
        import uuid
        conv_id = str(uuid.uuid4())

        # Store the conversation
        conversations[conv_id] = conversation

        return jsonify({"conversation_id": conv_id, "model": model_id})

    except llm.UnknownModelError:
        return jsonify({"error": f"Unknown model: {model_id}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/conversation/<conversation_id>/prompt', methods=['POST'])
def conversation_prompt(conversation_id):
    """Send a prompt to an existing conversation"""
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404

    data = request.json
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400

    conversation = conversations[conversation_id]

    try:
        response = conversation.prompt(data['prompt'])

        # Collect the full response by iterating through chunks
        full_text = ""
        for chunk in response:
            full_text += chunk

        result = {
            "text": full_text,
            "conversation_id": conversation_id
        }

        # Add usage information if available
        try:
            usage_data = response.usage()
            if usage_data and hasattr(usage_data, 'input'):
                result["usage"] = {
                    "input_tokens": usage_data.input,
                    "output_tokens": usage_data.output
                }
        except Exception as e:
            # Just log the error but don't fail the request
            print(f"Could not get usage data: {str(e)}")

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation_history(conversation_id):
    """Get the history of a conversation"""
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404

    conversation = conversations[conversation_id]

    # Extract responses from the conversation
    history = []
    for response in conversation.responses:
        # Get the full text of each response
        full_text = ""
        try:
            # Try to get text directly if already evaluated
            full_text = response.text()
        except:
            # Otherwise iterate through chunks
            for chunk in response:
                full_text += chunk

        history.append({
            "prompt": response.prompt,
            "response": full_text
        })

    return jsonify({
        "conversation_id": conversation_id,
        "history": history
    })


@app.route('/conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404

    del conversations[conversation_id]
    return jsonify({"status": "deleted", "conversation_id": conversation_id})


if __name__ == '__main__':
    print(
        f"Starting server with\n * DEFAULT_MODEL_ID: {DEFAULT_MODEL_ID} \n * MAX_TOKENS: {MAX_TOKENS}")
    # Set this to your desired host/port
    app.run(host='127.0.0.1', port=5000, debug=True)
