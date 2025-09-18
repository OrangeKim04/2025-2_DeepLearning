from flask import Flask, Response
from data_manager import data_manager

app = Flask(__name__)

@app.route('/report.txt')
def report_txt():
    """카카오톡과 동일한 리포트 원문을 그대로 반환"""
    data = data_manager.get_fresh_data()
    return Response(data.get('report_text', ''), mimetype='text/plain; charset=utf-8')

if __name__ == '__main__':
    print("🚀 웹 서버 시작 중... (카카오톡 링크용)")
    app.run(debug=True, host='0.0.0.0', port=5000)
