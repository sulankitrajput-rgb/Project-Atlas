from flask import Flask, request, jsonify
from flask_cors import CORS

import requests
import os
import base64

app = Flask(__name__)
CORS(app)

# ==========================
# API KEYS
# ==========================
GROQ_KEY = os.getenv("GROQ_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

print("===== PROJECT ATLAS =====")
print("Groq      :", "Loaded" if GROQ_KEY else "Missing")
print("Gemini    :", "Loaded" if GEMINI_KEY else "Missing")
print("DeepSeek  :", "Loaded" if DEEPSEEK_KEY else "Missing")
print("OpenAI    :", "Loaded" if OPENAI_KEY else "Missing")


# ==========================
# HOME PAGE
# ==========================
@app.route("/", methods=["GET"])
@app.route("/atlas", 
methods=["GET"])
def atlas():
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Project Atlas</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <script>

async function askAtlas() {

    const question = window.document.getElementById("question").value.trim();
    const result = window.document.getElementById("result");
    const loading = window.document.getElementById("loading");

    if (!question) {
        alert("Please enter a question.");
        return;
    }

    loading.style.display = "block";
    result.innerHTML = "";

    try {

        const response = await fetch("/compare", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "text/html"
            },
            body: JSON.stringify({
                question: question,
                image: ""
            })
        });

        const data = await response.text();

        if (!response.ok) {

            result.innerHTML =
                "<div class='card'>" +
                "<b>Error:</b><br>" +
                data +
                "</div>";

        } else {

            result.innerHTML = data;

        }

    } catch (error) {

        result.innerHTML =
            "<div class='card'>" +
            "<b>Connection Error:</b><br>" +
            error.message +
            "</div>";

    } finally {

        loading.style.display = "none";

    }
}

</script>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: linear-gradient(135deg, #eef4ff, #f8fbff);
    color: #172033;
    min-height: 100vh;
}

.container {
    width: 90%;
    max-width: 1000px;
    margin: 50px auto;
}

h1 {
    text-align: center;
    font-size: 42px;
    margin-bottom: 8px;
    color: #172554;
    letter-spacing: 2px;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 16px;
    margin-bottom: 35px;
}

textarea {
    width: 100%;
    min-height: 140px;
    padding: 20px;
    border: 2px solid #dbe4f0;
    border-radius: 16px;
    background: white;
    font-size: 17px;
    resize: vertical;
    outline: none;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.06);
}

textarea:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

button {
    width: 100%;
    margin-top: 18px;
    padding: 17px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    font-size: 17px;
    font-weight: bold;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);
}

button:active {
    transform: translateY(0);
}

#loading {
    display: none;
    text-align: center;
    margin: 25px 0;
    color: #475569;
    font-weight: bold;
}

#result {
    margin-top: 30px;
}

.result-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
    border-left: 5px solid #2563eb;
    overflow-x: auto;
}

.result-card pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 15px;
    line-height: 1.7;
    margin: 0;
}

@media (max-width: 600px) {

    .container {
        width: 94%;
        margin: 30px auto;
    }

    h1 {
        font-size: 30px;
    }

    textarea {
        min-height: 120px;
        font-size: 15px;
    }

    button {
        font-size: 15px;
    }
}

</style>
</head>

<body>

<div class="header">
    <h1>PROJECT ATLAS</h1>
    <p>AI COMPARISON</p>
</div>

<div class="container">

    <textarea id="question"
        placeholder="Ask Project Atlas anything..."></textarea>

    <button onclick="askAtlas()">
        COMPARE AI MODELS
    </button>

    <div id="loading">
         Comparing AI models...
    </div>
    
    <div id="result"></div>

</div>

</body>
</html>
"""


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
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    return {"answer": result["choices"][0]["message"]["content"]}


# ==========================
# GEMINI (UPDATED)
# ==========================
def ask_gemini(question, image=""):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_KEY
    }

    if image and image.startswith("http"):
        image_response = requests.get(image, timeout=30)
        image_response.raise_for_status()

        image_data = base64.b64encode(
            image_response.content
        ).decode("utf-8")

        body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": question
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ]
                }
            ]
        }

    else:
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

    try:
        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=60
        )

        if response.status_code != 200:
            return {
                "error": response.text
            }

        result = response.json()

        candidates = result.get("candidates", [])

        if not candidates:
            return {
                "error": "No Gemini answer returned."
            }

        parts = candidates[0].get(
            "content", {}
        ).get(
            "parts", []
        )

        if not parts:
            return {
                "error": "Gemini returned no text."
            }

        return {
            "answer": parts[0].get("text", "")
        }

    except Exception as e:
        return {
            "error": f"Gemini request failed: {str(e)}"
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

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    return {"answer": result["choices"][0]["message"]["content"]}

def ask_claude(question):

    url = "https://api.anthropic.com/v1/messages"

    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    body = {
        "model": "claude-3-5-haiku-latest",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()

    return {
        "answer": result["content"][0]["text"]
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

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    return {"answer": result["choices"][0]["message"]["content"]}


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

    elif model == "claude":
        result = ask_claude(question)
       
    else:
        result = ask_groq(question)

    return jsonify(result)

@app.route("/compare", methods=["POST"])
def compare():
    print("===== COMPARE TEST =====")
    print("Content-Type:", request.content_type)
    print("Raw:", request.get_data(as_text=True))

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No valid JSON recevied"}), 400

    question = data.get("question", "")
    image = data.get("image","")

    try:
        chatgpt = ask_openai(question)
    except Exception as e:
        chatgpt = {"error": str(e)}

    try:
        gemini = ask_gemini(question, image)
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

final_answer = f"""
<div class="compare-grid">

    <div class="ai-card">
        <h2> ChatGPT</h2>
        <div class="ai-answer">
            {get_text(chatgpt)}
        </div>
    </div>

    <div class="ai-card">
        <h2> Gemini</h2>
        <div class="ai-answer">
            {get_text(gemini)}
        </div>
    </div>

    <div class="ai-card">
        <h2> Groq</h2>
        <div class="ai-answer">
            {get_text(groq)}
        </div>
    </div>

    <div class="ai-card">
        <h2> Claude</h2>
        <div class="ai-answer">
            {get_text(claude)}
        </div>
    </div>

    <div class="ai-card">
        <h2> DeepSeek</h2>
        <div class="ai-answer">
            {get_text(deepseek)}
        </div>
    </div>

</div>
"""

return final_answer


def get_text(response):
    if not isinstance(response, dict):
        return str(response)

    # Normal answer
    if "answer" in response:
        return response["answer"]
        
    # Error handling
    if "error" in response:
        error = response["error"]

    if isinstance(error, dict):
        error = str(error)

    if "credit balance is too low" in error.lower():
        return "❌ API balance exhausted. Please recharge Claude."

    elif "insufficient balance" in error.lower():
        return "❌ API balance exhausted."

    elif "503" in error or "UNAVAILABLE" in error:
        return "⚠️ Service is temporarily unavailable."

    else:
        return "❌ " + error

    final_answer = f"""
<html>
<head>
<style>
body {{
    font-family: Arial, sans-serif;
    background:#f3f6fb;
    margin:20px;
}}

h1 {{
    text-align:center;
    color:#1f4ed8;
}}

.question {{
    background:white;
    padding:15px;
    border-radius:10px;
    margin-bottom:20px;
    box-shadow:0 2px 5px rgba(0,0,0,.1);
}}

.card {{
    background:white;
    margin:15px 0;
    padding:15px;
    border-radius:12px;
    box-shadow:0 2px 8px rgba(0,0,0,.12);
}}

.title {{
    font-size:22px;
    font-weight:bold;
    margin-bottom:10px;
}}

.chatgpt {{border-left:6px solid #10a37f;}}
.gemini {{border-left:6px solid #4285F4;}}
.groq {{border-left:6px solid #FF6B00;}}
.claude {{border-left:6px solid #D97706;}}
.deepseek {{border-left:6px solid #7C3AED;}}

pre {{
    white-space:pre-wrap;
    font-family:Arial;
}}
</style>
</head>

<body>

<h1> PROJECT ATLAS</h1>

<div class="question">
<h2>Question</h2>
<pre>{question}</pre>
</div>

<div class="card chatgpt">
<div class="title"> ChatGPT</div>
<pre>{get_text(chatgpt)}</pre>
</div>

<div class="card gemini">
<div class="title"> Gemini</div>
<pre>{get_text(gemini)}</pre>
</div>

<div class="card groq">
<div class="title"> Groq</div>
<pre>{get_text(groq)}</pre>
</div>

<div class="card claude">
<div class="title"> Claude</div>
<pre>{get_text(claude)}</pre>
</div>

<div class="card deepseek">
<div class="title"> DeepSeek</div>
<pre>{get_text(deepseek)}</pre>
</div>

</body>
</html>
"""
    return final_answer

# =========================
# STANDALONE PROJECT ATLAS
# =========================

@app.route("/", methods=["GET"])
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Project Atlas - AI Comparison</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f7fb;
        }

        .header {
            background: #1769ff;
            color: white;
            padding: 25px;
            text-align: center;
        }

        .header h1 {
            margin: 0;
            font-size: 32px;
        }

        .header p {
            margin: 8px 0 0;
            font-size: 17px;
        }

        .container {
            max-width: 900px;
            margin: 30px auto;
            padding: 20px;
        }

        textarea {
            width: 100%;
            height: 120px;
            padding: 15px;
            font-size: 17px;
            border: 1px solid #ccc;
            border-radius: 10px;
            box-sizing: border-box;
            resize: vertical;
        }

        button {
            width: 100%;
            margin-top: 15px;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            color: white;
            background: #1769ff;
            border: none;
            border-radius: 10px;
            cursor: pointer;
        }

        button:hover {
            background: #0d55d9;
        }

        #loading {
            display: none;
            text-align: center;
            margin: 25px;
            font-size: 18px;
        }

        #result {
            margin-top: 30px;
        }

        .card {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }

        .title {
            font-size: 21px;
            font-weight: bold;
            margin-bottom: 12px;
        }

        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
        }

        .footer {
            text-align: center;
            color: #777;
            margin: 30px;
        }
    </style>
</head>

<body>

    <div class="header">
        <h1>PROJECT ATLAS</h1>
        <p>AI COMPARISON</p>
    </div>

    <div class="container">

        <textarea id="question"
            placeholder="Ask Project Atlas anything..."></textarea>

        <button onclick="askAtlas()">
            COMPARE AI MODELS
        </button>

        <div id="loading">
             Comparing AI models...
        </div>

        <div id="result"></div>

    </div>

    <div class="footer">
        Project Atlas • AI Comparison
    </div>

<script>

async function askAtlas() {

    const question =
        document.getElementById("question").value.trim();

    const result =
        document.getElementById("result");

    const loading =
        document.getElementById("loading");

    if (!question) {
        alert("Please enter a question.");
        return;
    }

    loading.style.display = "block";
    result.innerHTML = "";

    try {

        const response = await fetch("/compare", {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Accept": "text/html"
            },

            body: JSON.stringify({
                question: question,
                image: ""
            })
        });

        const data = await response.text();

        if (!response.ok) {
            result.innerHTML =
                "<div class='card'>" +
                "<b>Error:</b><br>" +
                data +
                "</div>";
        } else {
            result.innerHTML = data;
        }

    } catch (error) {

        result.innerHTML =
            "<div class='card'>" +
            "<b>Connection error:</b><br>" +
            error.message +
            "</div>";

    } finally {

        loading.style.display = "none";
    }
}

</script>

</body>
</html>
"""

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
