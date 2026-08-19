from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import base64
from html import escape

app = Flask(__name__)
CORS(app)

# ============================================================
# PROJECT ATLAS - API KEYS
# ============================================================

GROQ_KEY = os.getenv("GROQ_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")


# ============================================================
# HELPER
# ============================================================

def get_text(response):
    if response is None:
        return "No response."

    if not isinstance(response, dict):
        return str(response)

    if "answer" in response:
        return str(response["answer"])

    if "error" in response:
        error = response["error"]

        if isinstance(error, dict):
            error = error.get("message", str(error))

        return "❌ " + str(error)

    return str(response)


# ============================================================
# GROQ
# ============================================================

def ask_groq(question):

    if not GROQ_KEY:
        return {"error": "GROQ_KEY is not configured."}

    try:

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            },
            timeout=60
        )

        if response.status_code != 200:
            return {"error": response.text}

        data = response.json()

        choices = data.get("choices", [])

        if not choices:
            return {"error": "Groq returned no answer."}

        return {
            "answer": choices[0]["message"]["content"]
        }

    except Exception as e:
        return {"error": str(e)}


# ============================================================
# GEMINI
# ============================================================

def ask_gemini(question, image=""):

    if not GEMINI_KEY:
        return {"error": "GEMINI_KEY is not configured."}

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-2.5-flash:generateContent"
    )

    try:

        parts = [
            {
                "text": question
            }
        ]

        if image and image.startswith("http"):

            image_response = requests.get(
                image,
                timeout=30
            )

            image_response.raise_for_status()

            image_data = base64.b64encode(
                image_response.content
            ).decode("utf-8")

            parts.append(
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                }
            )

        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_KEY
            },
            json={
                "contents": [
                    {
                        "parts": parts
                    }
                ]
            },
            timeout=60
        )

        if response.status_code != 200:
            return {"error": response.text}

        data = response.json()

        candidates = data.get("candidates", [])

        if not candidates:
            return {"error": "Gemini returned no answer."}

        content = candidates[0].get("content", {})

        parts = content.get("parts", [])

        if not parts:
            return {"error": "Gemini returned no text."}

        text = parts[0].get("text", "")

        return {
            "answer": text or "Gemini returned an empty answer."
        }

    except Exception as e:
        return {"error": str(e)}


# ============================================================
# CHATGPT / OPENAI
# ============================================================

def ask_openai(question):

    if not OPENAI_KEY:
        return {"error": "OPENAI_KEY is not configured."}

    try:

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4.1-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            },
            timeout=60
        )

        if response.status_code != 200:
            return {"error": response.text}

        data = response.json()

        choices = data.get("choices", [])

        if not choices:
            return {"error": "ChatGPT returned no answer."}

        return {
            "answer": choices[0]["message"]["content"]
        }

    except Exception as e:
        return {"error": str(e)}


# ============================================================
# CLAUDE
# ============================================================

def ask_claude(question):

    if not ANTHROPIC_KEY:
        return {"error": "ANTHROPIC_KEY is not configured."}

    try:

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-5-haiku-latest",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            },
            timeout=60
        )

        if response.status_code != 200:
            return {"error": response.text}

        data = response.json()

        content = data.get("content", [])

        if not content:
            return {"error": "Claude returned no answer."}

        return {
            "answer": content[0].get(
                "text",
                "Claude returned an empty answer."
            )
        }

    except Exception as e:
        return {"error": str(e)}


# ============================================================
# DEEPSEEK
# ============================================================

def ask_deepseek(question):

    if not DEEPSEEK_KEY:
        return {"error": "DEEPSEEK_KEY is not configured."}

    try:

        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            },
            timeout=60
        )

        if response.status_code != 200:
            return {"error": response.text}

        data = response.json()

        choices = data.get("choices", [])

        if not choices:
            return {"error": "DeepSeek returned no answer."}

        return {
            "answer": choices[0]["message"]["content"]
        }

    except Exception as e:
        return {"error": str(e)}


# ============================================================
# SINGLE MODEL
# ============================================================

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "No valid JSON received."
        }), 400

    question = data.get("question", "").strip()

    model = data.get(
        "model",
        "groq"
    ).lower()

    if not question:
        return jsonify({
            "error": "Question is empty."
        }), 400

    if model == "groq":

        result = ask_groq(question)

    elif model == "gemini":

        result = ask_gemini(question)

    elif model == "chatgpt":

        result = ask_openai(question)

    elif model == "claude":

        result = ask_claude(question)

    elif model == "deepseek":

        result = ask_deepseek(question)

    else:

        return jsonify({
            "error": f"Unknown model: {model}"
        }), 400

    return jsonify(result)


# ============================================================
# COMPARE ALL AI MODELS
# ============================================================

@app.route("/compare", methods=["POST"])
def compare():

    print("===== PROJECT ATLAS COMPARE =====")

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "No valid JSON received."
        }), 400

    question = data.get(
        "question",
        ""
    ).strip()

    image = data.get(
        "image",
        ""
    )

    if not question:

        return jsonify({
            "error": "Question is empty."
        }), 400

    # --------------------------------------------------------
    # CALL ALL FIVE MODELS
    # --------------------------------------------------------

    try:
        chatgpt = ask_openai(question)
    except Exception as e:
        chatgpt = {"error": str(e)}

    try:
        gemini = ask_gemini(
            question,
            image
        )
    except Exception as e:
        gemini = {"error": str(e)}

    try:
        groq = ask_groq(question)
    except Exception as e:
        groq = {"error": str(e)}

    try:
        claude = ask_claude(question)
    except Exception as e:
        claude = {"error": str(e)}

    try:
        deepseek = ask_deepseek(question)
    except Exception as e:
        deepseek = {"error": str(e)}

    # --------------------------------------------------------
    # CLEAN RESULTS
    # --------------------------------------------------------

    chatgpt_text = get_text(chatgpt)
    gemini_text = get_text(gemini)
    groq_text = get_text(groq)
    claude_text = get_text(claude)
    deepseek_text = get_text(deepseek)

    # --------------------------------------------------------
    # HTML RESULT
    # --------------------------------------------------------

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<style>

body {{
    margin: 0;
    padding: 20px;
    background: #f3f6fb;
    font-family: Arial, sans-serif;
}}

.question-box {{
    background: white;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 25px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
}}

.question-box b {{
    color: #1769ff;
}}

.compare-grid {{
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));
    gap: 20px;
}}

.ai-card {{
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.09);
    border-top: 5px solid #1769ff;
    min-width: 0;
}}

.ai-card h2 {{
    margin-top: 0;
    color: #172554;
}}

.ai-card pre {{
    margin: 0;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    word-break: break-word;
    font-family: Arial, sans-serif;
    font-size: 15px;
    line-height: 1.6;
    color: #263244;
}}

@media (max-width: 700px) {{

    .compare-grid {{
        grid-template-columns: 1fr;
    }}

}}

</style>

</head>

<body>

<div class="question-box">

<b>Question:</b><br>

{escape(question)}

</div>

<div class="compare-grid">

<div class="ai-card">

<h2>ChatGPT</h2>

<pre>{escape(chatgpt_text)}</pre>

</div>


<div class="ai-card">

<h2>Gemini</h2>

<pre>{escape(gemini_text)}</pre>

</div>


<div class="ai-card">

<h2>Groq</h2>

<pre>{escape(groq_text)}</pre>

</div>


<div class="ai-card">

<h2>Claude</h2>

<pre>{escape(claude_text)}</pre>

</div>


<div class="ai-card">

<h2>DeepSeek</h2>

<pre>{escape(deepseek_text)}</pre>

</div>

</div>

</body>

</html>
"""


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/", methods=["GET"])
@app.route("/atlas", methods=["GET"])
def home():

    return """
<!DOCTYPE html>

<html>

<head>

<title>Project Atlas</title>

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f7fb;
}}

.header {{
    background: #1769ff;
    color: white;
    padding: 30px 20px;
    text-align: center;
}}

.header h1 {{
    margin: 0;
    font-size: 34px;
}}

.header p {{
    margin-top: 8px;
}}

.container {{
    width: 92%;
    max-width: 1000px;
    margin: 30px auto;
}}

textarea {{
    width: 100%;
    min-height: 140px;
    padding: 18px;
    font-size: 17px;
    border: 1px solid #ccd5e1;
    border-radius: 12px;
    resize: vertical;
}}

button {{
    width: 100%;
    margin-top: 15px;
    padding: 17px;
    background: #1769ff;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
}}

button:hover {{
    background: #0d55d9;
}}

#loading {{
    display: none;
    text-align: center;
    margin: 25px;
    font-weight: bold;
}}

#result {{
    margin-top: 30px;
}}

</style>

</head>

<body>

<div class="header">

<h1>PROJECT ATLAS</h1>

<p>AI COMPARISON</p>

</div>


<div class="container">

<textarea
id="question"
placeholder="Ask Project Atlas anything..."
></textarea>


<button onclick="askAtlas()">

COMPARE AI MODELS

</button>


<div id="loading">

Comparing AI models...

</div>


<div id="result"></div>

</div>


<script>

async function askAtlas() {{

    const question =
        document
        .getElementById("question")
        .value
        .trim();

    const result =
        document
        .getElementById("result");

    const loading =
        document
        .getElementById("loading");


    if (!question) {{

        alert("Please enter a question.");

        return;

    }}


    loading.style.display = "block";

    result.innerHTML = "";


    try {{

        const response =
            await fetch(
                "/compare",
                {{
                    method: "POST",

                    headers: {{
                        "Content-Type":
                            "application/json"
                    }},

                    body: JSON.stringify({{
                        question: question,
                        image: ""
                    }})
                }}
            );


        const data =
            await response.text();


        if (!response.ok) {{

            result.innerHTML =
                "<div class='question-box'>" +
                "<b>Error:</b><br>" +
                data +
                "</div>";

        }} else {{

            result.innerHTML = data;

        }}

    }} catch (error) {{

        result.innerHTML =
            "<div class='question-box'>" +
            "<b>Connection error:</b><br>" +
            error.message +
            "</div>";

    }} finally {{

        loading.style.display = "none";

    }}

}}

</script>

</body>

</html>
"""


# ============================================================
# TEST
# ============================================================

@app.route("/test", methods=["POST"])
def test():

    return request.get_data(
        as_text=True
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                5000
            )
        )
    )
