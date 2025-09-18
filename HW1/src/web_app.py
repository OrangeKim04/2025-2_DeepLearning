from flask import Flask, Response
from data_manager import data_manager

app = Flask(__name__)

@app.route('/report.txt')
def report_txt():
    """카카오톡에서 보낸 리포트 파일을 HTML로 반환 (모바일 호환)"""
    try:
        # 저장된 리포트 파일 읽기 (카카오톡과 동일한 내용)
        with open('report.txt', 'r', encoding='utf-8') as f:
            report_text = f.read()
    except FileNotFoundError:
        # 파일이 없으면 기본 메시지
        report_text = "리포트 파일이 없습니다. 먼저 카카오톡 메시지를 전송해주세요."
    
    # HTML로 포맷팅 (모바일에서도 잘 보이도록)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>주식 분석 리포트</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #fff;
                margin: 0;
                padding: 20px;
                max-width: 100%;
                word-wrap: break-word;
            }}
            pre {{
                white-space: pre-wrap;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.4;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                overflow-x: auto;
            }}
            @media (max-width: 768px) {{
                body {{
                    padding: 10px;
                    font-size: 16px;
                }}
                pre {{
                    font-size: 13px;
                    padding: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <pre>{report_text}</pre>
    </body>
    </html>
    """
    
    return Response(html_content, mimetype='text/html; charset=utf-8')

if __name__ == '__main__':
    print("🚀 웹 서버 시작 중... (카카오톡 링크용)")
    app.run(debug=True, host='0.0.0.0', port=5000)
