from flask import Flask,request,jsonify
import requests
import os 

app = Flask(__name__)

GROQ_KEY = os.getenv("GROQ_KEY")


import json 

@app.route("/")   
def home():
  return "Project Atlas is runing!" 

@app.route("/ask",methods=["POST"])
def ask():

  import json

  data = request.get_json()

  if not data:
    return jsonify({"error":"No JSON received"}), 400

  question = data.get("question")
  
  headers = {
    "Authorization":f"Bearer {GROQ_KEY}",
    "Content-Type": "application/json"
  }
  body = {
    "model": "llama-3.3-70b-versatile",
    "messages":[
      {
        "role":"user",
        "content":question
      }
    ]
  }
  response = requests.post(

  "https://api.groq.com/openai/v1/chat/completions",
  headers=headers,
  json=body
)

result = response.json()

if "choices" not in result:
  return jsonify(result), 500
  
  answer = result["choices"][0]["message"]["content"]
  
  return jsonify({"answer": answer})

if __name__=="__main__":
  app.run(host="0.0.0.0",port=5000)
          
        
  
  
  

  
