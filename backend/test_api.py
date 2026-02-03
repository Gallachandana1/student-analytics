import requests
import pandas as pd
import io
import time

BASE_URL = 'http://127.0.0.1:5000'

def test_home():
    print("Testing Health Endpoint...")
    try:
        resp = requests.get(BASE_URL + '/api/status')
        assert resp.status_code == 200
        print("[OK] Health endpoint accessible")
    except Exception as e:
        print(f"[FAIL] Failed to reach health endpoint: {e}")

def test_upload():
    print("\nTesting Upload Endpoint...")
    # Create sample CSV
    csv_content = """student_id,attendance,study_hours,previous_grades,assignments_completed,participation
STU001,90,20,85,95,3
STU002,50,5,45,40,1
STU003,75,15,70,80,2
"""
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    
    try:
        resp = requests.post(BASE_URL + '/api/upload', files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data['total_students'] == 3
        print("[OK] Data uploaded successfully (3 students)")
    except Exception as e:
        print(f"[FAIL] Upload failed: {e}")

def test_dashboard():
    print("\nTesting Dashboard Endpoint...")
    try:
        resp = requests.get(BASE_URL + '/api/dashboard')
        assert resp.status_code == 200
        data = resp.json()
        assert data['stats']['total_students'] >= 3
        print("[OK] Dashboard stats are valid")
    except Exception as e:
        print(f"[FAIL] Dashboard check failed: {e}")

def test_prediction():
    print("\nTesting Prediction Endpoint...")
    payload = {
        "attendance": 85,
        "study_hours": 20,
        "previous_grades": 80,
        "assignments_completed": 90,
        "participation": 3
    }
    try:
        resp = requests.post(BASE_URL + '/api/predict', json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert 'predicted_score' in data
        print(f"[OK] Prediction success: Score {data['predicted_score']}")
    except Exception as e:
        print(f"[FAIL] Prediction failed: {e}")

def test_export():
    print("\nTesting Export Endpoint...")
    try:
        resp = requests.get(BASE_URL + '/api/export')
        if resp.status_code != 200:
            print(f"Export Error: {resp.status_code} - {resp.text}")
        assert resp.status_code == 200
        content_type = resp.headers.get('Content-Type', '')
        if 'text/csv' not in content_type:
            print(f"Wrong Content-Type: {content_type}")
        assert 'text/csv' in content_type
        print("[OK] Export success")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[FAIL] Export failed: {e}")

if __name__ == '__main__':
    print("[WAIT] Waiting for server to be ready (ensure you ran 'python backend/app.py')...")
    time.sleep(2)
    test_home()
    test_upload()
    test_dashboard()
    test_prediction()
    test_export()
