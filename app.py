from flask import Flask,request,jsonify

app = Flask(__name__)

@app.route("/")   
def home():
  return "Project Atlas is runing!" 

@app.route("/ask",methods=["POST"])
def ask():
  question = request.get_data(as_text=True)
  
  return jsonify({
  "gemini":"Gemini received:" + question,
  "groq":"Groq recevied:"+ question,
  "deepseek":"DeepSeek recevied:" + question
})

if __name__ == "__main__":
  app.run(host="0.0.0.0",port=5000)
  
  

  
