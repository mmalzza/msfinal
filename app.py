from flask import Flask, jsonify, request
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

openai.api_key = "YOUR_AZURE_OPENAI_KEY"

@app.route('/userinfo', methods=['GET'])
def get_user_info():
    return jsonify({
        'name': 'John Doe',
        'nationality': '필리핀',
        'passport': 'AB1234567',
        'visaType': 'E-9 (비전문취업)',
        'entryDate': '2024-07-31',
        'visaExpiry': '2025-07-30'
    })

@app.route('/update', methods=['POST'])
def update_info():
    data = request.json
    print('Received from client:', data)
    return jsonify({'message': '정보 업데이트 완료'})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    response = openai.ChatCompletion.create(
        engine="gpt-4",  # Azure에서 설정한 deployment 이름
        messages=[
            {"role": "system", "content": "출입국/체류 관련 전문 챗봇입니다."},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=1000
    )

    answer = response["choices"][0]["message"]["content"]
    return jsonify({"reply": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
