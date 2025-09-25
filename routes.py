from flask import Flask, render_template, request, jsonify
from recognizer import GestureRecognizer

app = Flask(__name__)

gesture_recognizer = GestureRecognizer()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.get_json()
    img_base64 = data.get("image")
    if not img_base64:
        return jsonify({"error": "No image data"}), 400

    result = gesture_recognizer.recognize(img_base64)
    return jsonify({
        "gesture": result["gesture"] or "",
        "current_word": result["current_word"],
        "current_sentence": result["current_sentence"],
    })

@app.route("/space", methods=["POST"])
def space():
    gesture_recognizer.finalize_word()
    return jsonify({"message": "Space added."})

@app.route("/stop", methods=["POST"])
def stop():
    final_sentence = gesture_recognizer.finalize_sentence()
    return jsonify({"final_sentence": final_sentence})

if __name__ == "__main__":
    app.run()
