import json
import os
from flask import request, jsonify


def create_assistant(client, knowledge_path):
    assistant_file_path = 'assistant.json'

    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("➡️➡️➡️ Loaded existing assistant ID. ⬅️⬅️⬅️")
    else:
        file = client.files.create(file=open(knowledge_path, "rb"),
                                   purpose='assistants')

        assistant = client.beta.assistants.create(
            name="Test-Assistant",
            instructions="""
              You will answer on question from your knowledge.
              """,
            model="gpt-4-1106-preview",
            tools=[{
                "type": "retrieval"
            }],
            file_ids=[file.id])

        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("➡️➡️➡️ Created a new assistant and saved the ID. ⬅️⬅️⬅️")

        assistant_id = assistant.id

    return assistant_id


def run_assistant(client, assistant_id):
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')

    if not thread_id:
        print("Error: Missing thread_id ⛔")  # Debugging line
        return jsonify({"error": "Missing thread_id"}), 400

    print(f"Received message: {user_input} for thread ID: {thread_id}")  # Debugging line

    # Add the user's message to the thread
    client.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content=user_input)

    # Run the Assistant
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                          assistant_id=assistant_id)

    return thread_id, run.id
