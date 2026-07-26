from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GROQ_KEY = os.getenv("GROQ_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")

print("Project Atlas Started")
print("Groq key loaded:", GROQ_KEY[:10] if GROQ_KEY else "NOT FOUND")
print("DeepSeek key loaded:", DEEPSEEK_KEY[:10] if DEEPSEEK_KEY else "NOT FOUND")


@app.route("/")
def home():
    return "Project Atlas is running!"


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json(force=True)

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    question = data.get("question")
    model = data.get("model", "llama").lower()

    # -------------------------
    # DeepSeek
    # -------------------------
    if model == "deepseek":

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

    # -------------------------
    # Groq (Llama)
    # -------------------------
    else:

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

    print("URL:", url)
    print("AUTH:", repr(headers["Authorization"]))

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    print("Status:", response.status_code)
    print("Response:", response.text)

    if response.status_code != 200:
        return jsonify({
            "error": response.text
        }), response.status_code

    result = response.json()

    answer = result["choices"][0]["message"]["content"]

    return jsonify({
        "answer": answer
    })


@app.route("/test", methods=["POST"])
def test():
    return request.get_data(as_text=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
