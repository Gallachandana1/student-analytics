from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import io
import csv

# Import our new modules
from database import init_db, add_students, get_all_students, get_student_dataframe, clear_data
from model import StudentModel

app = Flask(__name__, static_folder='../frontend', static_url_path='')
# Enable CORS for frontend communication
CORS(app)

# Initialize
init_db()
student_model = StudentModel()

@app.route('/')
def home():
    """Serve the frontend application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/status')
def status():
    """Verify backend status"""
    return jsonify({
        'message': 'Student Success Prediction API',
        'version': '2.0',
        'status': 'running'
    })

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """Upload and process student data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files allowed'}), 400
        
        df = pd.read_csv(file)
        
        # --- Mapping Logic for sample_data.csv ---
        # Map CSV columns to our internal schema
        column_mapping = {
            'StudentID': 'student_id',
            'AttendanceRate': 'attendance',
            'StudyHoursPerWeek': 'study_hours',
            'PreviousGPA': 'previous_grades',
            'AssignmentScore': 'assignments_completed',
            'ParticipationScore': 'participation',
            'Major': 'major',
            'YearOfStudy': 'year_of_study',
            'Gender': 'gender',
            'Ethnicity': 'ethnicity',
            'ParentEducation': 'parent_education',
            'FamilyIncome': 'family_income'
        }
        
        # Check if it's the new format
        if 'StudentID' in df.columns:
            df = df.rename(columns=column_mapping)
            
            # Normalize GPA (4.0 scale) to percentage (100 scale)
            # Assuming max GPA is 4.0
            if 'previous_grades' in df.columns:
                df['previous_grades'] = df['previous_grades'] * 25
                
            # Normalize Participation Score (0-100) to 1-3 Level
            # 0-60: Low (1), 60-85: Medium (2), 85-100: High (3)
            if 'participation' in df.columns:
                conditions = [
                    (df['participation'] < 60),
                    (df['participation'] >= 60) & (df['participation'] < 85),
                    (df['participation'] >= 85)
                ]
                choices = [1, 2, 3]
                df['participation'] = np.select(conditions, choices, default=2)

        # Fallback for old simple format (validation)
        required_cols = ['student_id', 'attendance', 'study_hours', 
                        'previous_grades', 'assignments_completed']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_cols)}'
            }), 400
        
        # --- Data Cleaning ---
        # Fill missing numeric values with mean
        numeric_cols = ['attendance', 'study_hours', 'previous_grades', 'assignments_completed']
        for col in numeric_cols:
             if col in df.columns:
                 df[col] = df[col].fillna(df[col].mean())
        
        if 'participation' not in df.columns:
            df['participation'] = np.random.randint(1, 4, size=len(df))
            
        # Ensure new demographic columns exist even if not in input (for old CSVs)
        for col in ['major', 'year_of_study', 'gender', 'ethnicity', 'parent_education', 'family_income']:
            if col not in df.columns:
                df[col] = 'Unknown'

        # --- Performance Calculation ---
        if 'performance' not in df.columns or df['performance'].isnull().any():
             df['performance'] = (
                df['attendance'] * 0.25 +
                df['study_hours'] * 3 * 0.20 +
                df['previous_grades'] * 0.30 +
                df['assignments_completed'] * 0.15 +
                (df['participation'] / 3 * 100) * 0.10
            )
        
        # Clip performance to 0-100
        df['performance'] = df['performance'].clip(0, 100)

        # --- Risk Assessment ---
        df['risk_level'] = df['performance'].apply(
            lambda x: 'Low' if x >= 70 else 'Medium' if x >= 50 else 'High'
        )
        
        # --- Persistence ---
        # Select only columns that exist in our DB schema to avoid errors
        # (Assuming add_students handles extra columns gracefully or we filter them)
        count = add_students(df)
        
        # Train Model
        all_students_df = get_student_dataframe()
        student_model.train(all_students_df)
        
        return jsonify({
            'message': 'Data uploaded successfully',
            'total_students': count,
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
        
        # Use our model class for prediction
        predicted_score = student_model.predict(data)
        
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
        students = get_all_students()
        return jsonify({
            'total': len(students),
            'students': students
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard statistics"""
    try:
        df = get_student_dataframe()
        
        if df.empty:
            return jsonify({
                'message': 'No data available',
                'stats': {
                    'total_students': 0,
                    'average_performance': 0,
                    'at_risk_students': 0,
                    'high_performers': 0
                }
            }), 200
        
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
        df = get_student_dataframe()
        
        if df.empty:
            return jsonify({
                'message': 'No data available',
                'analytics': {}
            }), 200
        
        # Sample for scatter plots if too large
        plot_df = df.sample(min(len(df), 500)) if len(df) > 500 else df

        analytics = {
            'attendance_vs_performance': [
                {'x': row['attendance'], 'y': row['performance']}
                for _, row in plot_df.iterrows()
            ],
            'study_hours_vs_performance': [
                {'x': row['study_hours'], 'y': row['performance']}
                for _, row in plot_df.iterrows()
            ],
            'grades_vs_assignments': [
                {'x': row['previous_grades'], 'y': row['assignments_completed']}
                for _, row in plot_df.iterrows()
            ],
            'participation_distribution': {
                'Low': len(df[df['participation'] == 1]),
                'Medium': len(df[df['participation'] == 2]),
                'High': len(df[df['participation'] == 3])
            },
           'major_distribution': df['major'].value_counts().to_dict(),
           'feature_importance': student_model.get_feature_importance()
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_data():
    """Export student data as CSV"""
    try:
        students = get_all_students()
        if not students:
            return jsonify({'error': 'No data to export'}), 400

        # Create CSV in memory
        si = io.StringIO()
        cw = csv.DictWriter(si, fieldnames=students[0].keys())
        cw.writeheader()
        cw.writerows(students)
        output = si.getvalue()

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=student_analytics_export.csv"}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)