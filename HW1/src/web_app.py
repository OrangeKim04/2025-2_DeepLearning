from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
import pytz
from typing import Dict, List, Any
import pandas as pd

from data_manager import data_manager

app = Flask(__name__, template_folder='../templates')

# DataManager를 사용하므로 전역 변수 제거

def update_stock_data():
    """주식 데이터를 강제 새로고침하는 함수"""
    try:
        data_manager.force_refresh()
        return True
    except Exception as e:
        print(f"❌ 데이터 업데이트 실패: {e}")
        return False

@app.route('/')
def index():
    """메인 페이지"""
    data = data_manager.get_fresh_data()
    return render_template('index.html', 
                         kr_items=data['kr_items'],
                         us_items=data['us_items'],
                         news_summary=data['news_summary'],
                         last_update=data['last_update'],
                         has_data=bool(data['kr_items']))

@app.route('/api/update')
def api_update():
    """데이터 업데이트 API"""
    success = update_stock_data()
    data = data_manager.get_fresh_data()
    return jsonify({
        'success': success,
        'last_update': data['last_update'].isoformat() if data['last_update'] else None
    })

@app.route('/api/data')
def api_data():
    """주식 데이터 API"""
    data = data_manager.get_fresh_data()
    return jsonify({
        'last_update': data['last_update'].isoformat() if data['last_update'] else None,
        'kr_items': data['kr_items'],
        'us_items': data['us_items'],
        'news_summary': data['news_summary'],
        'report_text': data['report_text']
    })

@app.route('/api/report')
def api_report():
    """리포트 텍스트 API"""
    data = data_manager.get_fresh_data()
    return jsonify({
        'report_text': data['report_text'],
        'last_update': data['last_update'].isoformat() if data['last_update'] else None
    })

if __name__ == '__main__':
    # 서버 시작 시 초기 데이터 로드
    print("🚀 웹 서버 시작 중...")
    update_stock_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
