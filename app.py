from flask import Flask,request,jsonify
import requests
import os 

app = Flask(__name__)

GEMINI_KEY =os.getenv("GEMINI_KEY")
GROQ_KEY = os.getenv("GROQ_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")

import json 

@app.route("/")   
def home():
  return "Project Atlas is runing!" 

@app.route("/ask",methods=["POST"])
def ask():
  print("HEADER:", request.headers)
  print("BODY:",
        request.get_data(as_text=True))
                         return"Received"
          

  gemini = requests.post(

    f"htps://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
    json={
      "contents":[
        {
          "parts":[
            {"text":question}
          ]
        }
      ]
    }
  ).json()
  answer = gemini["candidates"][0]["content"]["parts"][0]["text"]
  return jsonify({
  "answer": answer
  })

if __name__=="__main__":
  app.run(host="0.0.0.0",port=5000,debug=True)
          
        
  
  
  

  
