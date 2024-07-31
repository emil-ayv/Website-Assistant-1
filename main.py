import os
from time import sleep
from flask import Flask, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import chatbot.functions as functions

# OpenAI API Key
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')


# -------- Start Flask app --------
app = Flask(__name__)
# Init client
client = OpenAI()  # should use env variable OPENAI_API_KEY in secrets (bottom left corner)
# Create new assistant or load existing
assistant_id = functions.create_assistant(client, knowledge_path="data/knowledge.docx")


# Start conversation thread
@app.route('/start', methods=['GET'])
def start_conversation():
    print("Starting a new conversation... 🛜")  # Debugging line
    thread = client.beta.threads.create()
    print(f"New thread created with ID: {thread.id}")  # Debugging line
    return jsonify({"thread_id": thread.id})


# Generate response
@app.route('/chat', methods=['POST'])
def chat():
    thread_id, run_id = functions.run_assistant(client, assistant_id)

    # Check if the Run requires action (function call)
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                       run_id=run_id)
        print(f"Run status: {run_status.status}")
        if run_status.status == 'completed':
            break
        sleep(1)  # Wait for a second before checking again

    # Retrieve and return the latest message from the assistant
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value

    print(f"Assistant response: {response}")  # Debugging line
    return jsonify({"response": response})


# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
