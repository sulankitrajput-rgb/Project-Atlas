from flask import Flask,request,jsonify
import requests
import os 

app = Flask(__name__)

GEMINI_KEY =os.getenev("GEMINI_KEY")
GROQ_KEY = os.getenv("GROQ_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")

@app.route("/")   
def home():
  return "Project Atlas is runing!" 

@app.route("/ask",methods=["POST"])
def ask():

  question = request.get_json()["question"]

  gemini = requests.post(

f"https:/generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    json={
      "contents":[{"parts":
      [{"text":question}]}]
       }
    ).json()
  return jsonify({
  "gemini": gemini
})

if __name__ == "__main__":
  app.run(host="0.0.0.0",port=5000)
  
  

  
