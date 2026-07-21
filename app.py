from flask import Flask,request,jsonify

app = Flask(__name__)

@app.route("/")   
def home():
  return "Project Atlas is runing!" 

@app.route("/ask",methods=["POST"])
def ask():
  data = request.get_json()
  question = data.get("quesion","")

  return jsonify({
  "gemini":"Gemini received:" + question,
  "groq":"Groq recevied:"+ question,
  "deepseek":"DeepSeek recevied:" + question
})

if __name__ == "__main__":
  app.run(host="0.0.0.0",port=5000)
  
  

  
