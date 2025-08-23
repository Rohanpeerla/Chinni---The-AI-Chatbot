import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env (only for local dev)
if os.path.exists(".env"):
    load_dotenv()

app = Flask(__name__)

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing! Set it in .env or Render.")

client = Groq(api_key=GROQ_API_KEY)

# Chat history (simple in-memory storage)
chat_history = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    chat_history.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=chat_history,
            max_tokens=500,
            temperature=0.7
        )
        bot_reply = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": bot_reply})
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear", methods=["POST"])
def clear():
    global chat_history
    chat_history = []
    return jsonify({"status": "Cleared"})

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8007))
    app.run(host="0.0.0.0", port=port, debug=False)