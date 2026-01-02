from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import os

app = Flask(__name__)
CORS(app)

# Global variables
model = None
scaler = None
student_data = []

def train_model(data):
    """Train the prediction model with student data"""
    global model, scaler
    
    df = pd.DataFrame(data)
    
    features = ['attendance', 'study_hours', 'previous_grades', 
                'assignments_completed', 'participation']
    
    if 'performance' not in df.columns:
        df['performance'] = (
            df['attendance'] * 0.25 +
            df['study_hours'] * 3 * 0.20 +
            df['previous_grades'] * 0.30 +
            df['assignments_completed'] * 0.15 +
            (df['participation'] / 3 * 100) * 0.10
        )
    
    X = df[features]
    y = df['performance']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    
    return True

@app.route('/')
def home():
    return jsonify({
        'message': 'Student Success Prediction API',
        'version': '1.0',
        'status': 'running'
    })

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """Upload and process student data"""
    global student_data
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files allowed'}), 400
        
        df = pd.read_csv(file)
        
        required_cols = ['student_id', 'attendance', 'study_hours', 
                        'previous_grades', 'assignments_completed']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_cols)}'
            }), 400
        
        if 'participation' not in df.columns:
            df['participation'] = np.random.randint(1, 4, size=len(df))
        
        df['performance'] = (
            df['attendance'] * 0.25 +
            df['study_hours'] * 3 * 0.20 +
            df['previous_grades'] * 0.30 +
            df['assignments_completed'] * 0.15 +
            (df['participation'] / 3 * 100) * 0.10
        )
        
        df['risk_level'] = df['performance'].apply(
            lambda x: 'Low' if x >= 70 else 'Medium' if x >= 50 else 'High'
        )
        
        student_data = df.to_dict('records')
        train_model(student_data)
        
        return jsonify({
            'message': 'Data uploaded successfully',
            'total_students': len(student_data),
            'columns': list(df.columns)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict student performance"""
    try:
        data = request.json
        
        required_fields = ['attendance', 'study_hours', 'previous_grades', 
                          'assignments_completed', 'participation']
        
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return jsonify({
                'error': f'Missing fields: {", ".join(missing_fields)}'
            }), 400
        
        features = np.array([[
            data['attendance'],
            data['study_hours'],
            data['previous_grades'],
            data['assignments_completed'],
            data['participation']
        ]])
        
        if model is not None and scaler is not None:
            features_scaled = scaler.transform(features)
            predicted_score = model.predict(features_scaled)[0]
        else:
            predicted_score = (
                data['attendance'] * 0.25 +
                data['study_hours'] * 3 * 0.20 +
                data['previous_grades'] * 0.30 +
                data['assignments_completed'] * 0.15 +
                (data['participation'] / 3 * 100) * 0.10
            )
        
        predicted_score = min(predicted_score, 100)
        
        if predicted_score >= 75:
            risk_level = 'Low'
            status = 'High Success Probability'
            recommendation = 'Student is on track for excellent performance!'
            color = 'success'
        elif predicted_score >= 50:
            risk_level = 'Medium'
            status = 'Moderate Success Probability'
            recommendation = 'Student may need additional support in some areas.'
            color = 'warning'
        else:
            risk_level = 'High'
            status = 'At-Risk Student'
            recommendation = 'Immediate intervention recommended.'
            color = 'danger'
        
        insights = []
        if data['attendance'] < 75:
            insights.append('Low attendance - recommend counseling')
        if data['study_hours'] < 10:
            insights.append('Insufficient study hours - suggest study plan')
        if data['assignments_completed'] < 70:
            insights.append('Low assignment completion - check engagement')
        if data['previous_grades'] < 60:
            insights.append('Struggling academically - consider tutoring')
        
        return jsonify({
            'predicted_score': round(predicted_score, 2),
            'risk_level': risk_level,
            'status': status,
            'recommendation': recommendation,
            'color': color,
            'insights': insights
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all student data"""
    try:
        if not student_data:
            return jsonify({
                'message': 'No data available',
                'students': []
            }), 200
        
        return jsonify({
            'total': len(student_data),
            'students': student_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard statistics"""
    try:
        if not student_data:
            return jsonify({
                'message': 'No data available',
                'stats': {
                    'total_students': 0,
                    'average_performance': 0,
                    'at_risk_students': 0,
                    'high_performers': 0
                }
            }), 200
        
        df = pd.DataFrame(student_data)
        
        stats = {
            'total_students': len(df),
            'average_performance': round(df['performance'].mean(), 2),
            'at_risk_students': len(df[df['performance'] < 50]),
            'high_performers': len(df[df['performance'] >= 75]),
            'average_attendance': round(df['attendance'].mean(), 2),
            'average_study_hours': round(df['study_hours'].mean(), 2)
        }
        
        performance_dist = {
            'Below 50': len(df[df['performance'] < 50]),
            '50-60': len(df[(df['performance'] >= 50) & (df['performance'] < 60)]),
            '60-70': len(df[(df['performance'] >= 60) & (df['performance'] < 70)]),
            '70-80': len(df[(df['performance'] >= 70) & (df['performance'] < 80)]),
            'Above 80': len(df[df['performance'] >= 80])
        }
        
        risk_dist = {
            'Low': len(df[df['risk_level'] == 'Low']),
            'Medium': len(df[df['risk_level'] == 'Medium']),
            'High': len(df[df['risk_level'] == 'High'])
        }
        
        return jsonify({
            'stats': stats,
            'performance_distribution': performance_dist,
            'risk_distribution': risk_dist
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for charts"""
    try:
        if not student_data:
            return jsonify({
                'message': 'No data available',
                'analytics': {}
            }), 200
        
        df = pd.DataFrame(student_data)
        
        analytics = {
            'attendance_vs_performance': [
                {'x': row['attendance'], 'y': row['performance']}
                for _, row in df.iterrows()
            ],
            'study_hours_vs_performance': [
                {'x': row['study_hours'], 'y': row['performance']}
                for _, row in df.iterrows()
            ],
            'correlation_matrix': {
                'attendance_performance': round(
                    df['attendance'].corr(df['performance']), 2
                ),
                'study_hours_performance': round(
                    df['study_hours'].corr(df['performance']), 2
                ),
                'assignments_performance': round(
                    df['assignments_completed'].corr(df['performance']), 2
                )
            }
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)