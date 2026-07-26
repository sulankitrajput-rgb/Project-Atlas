print("VERSION 25 JULY TEST")
from flask import Flask,request,jsonify
import requests
import os 

app = Flask(__name__)

GROQ_KEY = os.getenv("GROQ_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
print("Groq key loaded:",GROQ_KEY[:10] if GROQ_KEY else "NOT FOUND")

import json 

@app.route("/")   
def home():
  return "Project Atlas is runing!" 

@app.route("/ask",methods=["POST"])
def ask():

  import json

  data = request.get_json(force=True)

  if not data:
    return jsonify({"error":"No JSON received"}), 400

  question = data.get("question")
  model = data.get("model","llama")

  if model.lower() == "deepseek":
    headers = {
      "Authorization":f"Bearer {DEEPSEEK_KEY}",
      "Content-Type": "application/json"
    }
    url ="https://api.deepseek.com/chat/completions"
    body = {
      "model": "deepseek-chat",
      "messages": [
        {
          "role": "user",
          "content": question
        }
      ]
    }

  else:
    headers = {
      "Authorization":"Bearer" + GROQ_KEY,
      "Content-Type": "application/json"
    }
    url = "https://api.groq.com/openai/v1/chat/completions"
    body = {
      "model":"llama-3.3-70b-versatile",
      "messages": [
        {
          "role": "user",
          "content": question
        }
      ]
    }
    print(repr(headers["Authorization"]))
response = requests.post(
    url,
  headers=headers,
  json=body
)

  print(response.status_code)
  print(response.text)
  
  result = response.json()
  if "choices" not in result:
    return jsonify(result), 500
    
  answer = result["choices"][0]["message"]["content"]
  return jsonify({"answer": answer})

@app.route("/test",methods=["POST"])
def test():
  return request.get_data(as_text=True)
  

if __name__=="__main__":
  app.run(host="0.0.0.0",port=5000)
          
        
  
  
  

  
