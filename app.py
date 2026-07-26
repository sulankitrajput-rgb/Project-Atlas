from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ==========================
# API KEYS
# ==========================
GROQ_KEY = os.getenv("GROQ_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")

print("===== PROJECT ATLAS =====")
print("Groq      :", "Loaded" if GROQ_KEY else "Missing")
print("Gemini    :", "Loaded" if GEMINI_KEY else "Missing")
print("DeepSeek  :", "Loaded" if DEEPSEEK_KEY else "Missing")
print("OpenAI    :", "Loaded" if OPENAI_KEY else "Missing")


# ==========================
# HOME PAGE
# ==========================
@app.route("/")
def home():
    return "Project Atlas is running!"


# ==========================
# GROQ
# ==========================
def ask_groq(question):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()

    return {
        "answer": result["choices"][0]["message"]["content"]
    }

# ==========================
# GEMINI
# ==========================
def ask_gemini(question):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": question
                    }
                ]
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()

    return {
        "answer": result["candidates"][0]["content"]["parts"][0]["text"]
    }


# ==========================
# CHATGPT
# ==========================
def ask_openai(question):

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()

    return {
        "answer": result["choices"][0]["message"]["content"]
    }
    
# ==========================
# DEEPSEEK
# ==========================
def ask_deepseek(question):

    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()

    return {
        "answer": result["choices"][0]["message"]["content"]
    }


# ==========================
# ASK ROUTE
# ==========================
@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json(force=True)

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    question = data.get("question")
    model = data.get("model", "groq").lower()

    if model == "groq":
        result = ask_groq(question)

    elif model == "gemini":
        result = ask_gemini(question)

    elif model == "chatgpt":
        result = ask_openai(question)

    elif model == "deepseek":
        result = ask_deepseek(question)

    else:
        result = ask_groq(question)

    return jsonify(result)


# ==========================
# TEST ROUTE
# ==========================
@app.route("/test", methods=["POST"])
def test():
    return request.get_data(as_text=True)


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
