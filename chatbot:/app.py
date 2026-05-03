from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from flask import send_file
import os

app = Flask(__name__)

client = OpenAI(api_key= "API KEY IS REMOVED FOR SAFETY")

LOG_FILE = "logs.txt"

def log(text):
    with open(LOG_FILE, "a") as f:
        f.write(text + "\n")




def load_recent_messages(filename, max_turns=12):
    """
    Reads session file like:
      USER: ...
      BOT: ...
    Returns OpenAI messages list for last max_turns turns.
    """
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]

    pairs = []
    current_user = None

    for ln in lines:
        if ln.startswith("USER:"):
            current_user = ln.replace("USER:", "", 1).strip()
        elif ln.startswith("BOT:") and current_user is not None:
            bot = ln.replace("BOT:", "", 1).strip()
            pairs.append((current_user, bot))
            current_user = None

    pairs = pairs[-max_turns:]  # keep last N turns

    messages = []
    for u, b in pairs:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": b})

    return messages





@app.route("/")
def home():
    return render_template("index.html")




@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data["message"]
    session_id = data.get("session_id", "anonymous")

    log(f"[{session_id}] USER: {user_message}")

    # Each participant gets their own file
    filename = f"{session_id}.txt"

    # Save the user's message to the session file
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"USER: {user_message}\n")

    # MEMORY: load last messages from this session file
    recent = load_recent_messages(filename, max_turns=12)

    # Build full prompt (system + memory + latest user msg)
    messages = [
        {"role": "system", "content": "You are Athena, a helpful research chatbot. Keep answers clear and concise."},
        *recent,
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    bot_reply = response.choices[0].message.content

    # Save bot reply to the session file
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"BOT: {bot_reply}\n\n")

    log(f"[{session_id}] BOT: {bot_reply}")

    return jsonify({"reply": bot_reply})







@app.route("/test_ui")
def test_ui():
    return render_template("test_ui.html")

@app.route("/download/<session_id>")
def download_chat(session_id):
    filename = f"{session_id}.txt"
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
