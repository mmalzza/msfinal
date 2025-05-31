from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
