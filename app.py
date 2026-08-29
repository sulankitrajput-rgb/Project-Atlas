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
        return {
            "error": "GROQ_KEY is not configured."
        }

    try:

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": "openai/gpt-oss-20b",

                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ],

                "temperature": 0.7,

                "max_tokens": 2048
            },

            timeout=60
        )

        # -----------------------------
        # HANDLE RATE LIMIT
        # -----------------------------

        if response.status_code == 429:

            return {
                "error": "Groq is temporarily busy or rate-limited. Please try again in a few seconds."
            }

        # -----------------------------
        # HANDLE OTHER API ERRORS
        # -----------------------------

        if response.status_code != 200:

            try:
                error_data = response.json()

                error_message = (
                    error_data
                    .get("error", {})
                    .get("message", response.text)
                )

            except Exception:
                error_message = response.text

            return {
                "error": f"Groq API error: {error_message}"
            }

        # -----------------------------
        # READ JSON RESPONSE
        # -----------------------------

        data = response.json()

        choices = data.get("choices", [])

        if not choices:

            return {
                "error": "Groq returned no answer."
            }

        # -----------------------------
        # GET ANSWER
        # -----------------------------

        message = choices[0].get("message", {})

        answer = message.get("content", "")

        if not answer:

            return {
                "error": "Groq returned an empty answer."
            }

        return {
            "answer": answer
        }

    except requests.exceptions.Timeout:

        return {
            "error": "Groq took too long to respond. Please try again."
        }

    except requests.exceptions.RequestException as e:

        return {
            "error": f"Groq connection error: {str(e)}"
        }

    except Exception as e:

        return {
            "error": f"Groq error: {str(e)}"
        }

# ============================================================
# GEMINI
# ============================================================

def ask_gemini(question, image=None):

    if not GEMINI_KEY:
        return {"error": "GEMINI_KEY is not configured."}

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_KEY
    }

    try:
        # Text only
        if not image:
            payload = {
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

        # Text + image
        else:
            if isinstance(image, bytes):
                import base64
                image_data = base64.b64encode(image).decode("utf-8")
            else:
                image_data = image

                # Remove data URL prefix if present
                if "," in image_data and image_data.startswith("data:"):
                    image_data = image_data.split(",", 1)[1]

            payload = {
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

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=(5, 15)
        )

        if response.status_code != 200:
            return {
                "error": "Gemini API error: " + response.text
            }

        data = response.json()

        candidates = data.get("candidates", [])

        if not candidates:
            return {
                "error": "Gemini returned no answer."
            }

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])

        if not parts:
            return {
                "error": "Gemini returned no text."
            }

        text = parts[0].get("text", "")

        if not text:
            return {
                "error": "Gemini returned an empty answer."
            }

        return {
            "answer": text
        }

    except requests.exceptions.Timeout:
        return {
            "error": "Gemini request timed out."
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": "Gemini connection error: " + str(e)
        }

    except Exception as e:
        return {
            "error": "Gemini error: " + str(e)
        }

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
                "model": 
                "claude-3-5-haiku-latest",
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
    # CALL ALL FOUR MODELS
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

    # --------------------------------------------------------
    # CLEAN RESULTS
    # --------------------------------------------------------

    chatgpt_text = get_text(chatgpt)
    gemini_text = get_text(gemini)
    groq_text = get_text(groq)
    claude_text = get_text(claude)
 
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

</div>

</body>

</html>
"""


# ============================================================
# HOME PAGE
# ============================================================

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
    padding: 30px;
    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 34px;
}

.header p {
    margin: 10px 0 0;
    font-size: 18px;
}

.container {
    max-width: 900px;
    margin: 30px auto;
    padding: 20px;
}

/* QUESTION BOX */

textarea {
    width: 100%;
    height: 120px;
    padding: 15px;
    font-size: 17px;
    border: 1px solid #ccc;
    border-radius: 12px;
    box-sizing: border-box;
    resize: vertical;
}

/* STYLE AREA */

.style-label {
    display: block;
    margin-top: 20px;
    margin-bottom: 8px;
    font-size: 17px;
    font-weight: bold;
}

select {
    width: 100%;
    padding: 14px;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 10px;
    background: white;
    box-sizing: border-box;
}

/* BUTTON */

button {
    width: 100%;
    margin-top: 18px;
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

/* LOADING */

#loading {
    display: none;
    text-align: center;
    margin: 25px;
    font-size: 18px;
    font-weight: bold;
}

/* RESULTS */

#result {
    margin-top: 30px;
}

.compare-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
}

.ai-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    border-left: 5px solid #1769ff;
}

.ai-card h2 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 22px;
}

.ai-answer {
    overflow-x: auto;
}

pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    margin: 0;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.footer {
    text-align: center;
    color: #777;
    margin: 30px;
}

/* MOBILE */

@media (max-width: 600px) {

    .container {
        width: 94%;
        margin: 20px auto;
        padding: 10px;
    }

    .header h1 {
        font-size: 28px;
    }

    textarea {
        height: 120px;
    }

    button {
        font-size: 16px;
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


    <!-- QUESTION BOX -->

    <textarea
        id="question"
        placeholder="Ask Project Atlas anything..."
    ></textarea>


    <!-- STYLE OPTION -->

    <label class="style-label" for="style">
        Answer Style:
    </label>


    <select id="style">

        <option value="balanced">
            Balanced
        </option>

        <option value="simple">
            Simple
        </option>

        <option value="detailed">
            Detailed
        </option>

        <option value="creative">
            Creative
        </option>

    </select>


    <!-- COMPARE BUTTON -->

    <button onclick="askAtlas()">

        COMPARE AI MODELS

    </button>


    <!-- LOADING MESSAGE -->

    <div id="loading">

        Comparing AI models...

    </div>


    <!-- ANSWERS WILL APPEAR HERE -->

    <div id="result"></div>


</div>


<div class="footer">

    Project Atlas • AI Comparison

</div>


<script>

async function askAtlas() {

    const questionElement =
        document.getElementById("question");

    const styleElement =
        document.getElementById("style");

    const result =
        document.getElementById("result");

    const loading =
        document.getElementById("loading");

    const button =
        document.querySelector("button");

    const question =
        questionElement ? questionElement.value.trim() : "";

    const style =
        styleElement ? styleElement.value : "balanced";

    if (!question) {
        alert("Please enter a question.");
        return;
    }

    // Prevent multiple requests
    if (button) {
        button.disabled = true;
        button.innerText = "⏳ Thinking...";
    }

    loading.style.display = "block";
    loading.innerText = "🤖 Comparing AI models...";
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
                image: "",
                style: style
            })
        });

        // Get the complete server response
        const data = await response.text();

        // Only treat it as an error when HTTP itself failed
        if (!response.ok) {
            throw new Error(
                data || "Server returned an error."
            );
        }

        // Display the answer
        result.innerHTML = data;

    } catch (error) {

        console.error(
            "Project Atlas error:",
            error
        );

        result.innerHTML = `
            <div class="card">
                <h3>⚠️ Something went wrong</h3>
                <p>${error.message}</p>
            </div>
        `;

    } finally {

        // Always hide loading message
        loading.style.display = "none";

        // Re-enable button
        if (button) {
            button.disabled = false;
            button.innerText = "COMPARE AI MODELS";
        }
    }
}



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
