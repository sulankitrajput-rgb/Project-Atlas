from flask import Flask,request,jsonify

app=Flask(__name__)

@app.route("/")
def home():
  return"Project Atlas is running!"

@app.route("/ask",methods=["POST"])
def ask():
  data=request.get_json()
  question = data.get("question","")

return jsonify({
  "gemini":"Gemini recevied:"+question,
  "groq":"Groq recevied:"+question,
  "deepseek":"DeepSeek received:"+question
})

if__name__=="__main__":
  app.run(host="0.0.0.0",port=5000)

  
