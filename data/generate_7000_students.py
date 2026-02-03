import random

print("=" * 60)
print("  GENERATING 7000 STUDENT DATASET")
print("=" * 60)
print()

with open('student_data_7000.csv', 'w') as f:
    # Write header
    f.write('student_id,attendance,study_hours,previous_grades,assignments_completed,participation\n')
    
    # Generate 7000 students
    for i in range(1, 7001):
        student_id = f'STU{str(i).zfill(4)}'
        
        # Randomly assign student performance category
        category = random.random()
        
        if category < 0.20:  # 20% Excellent students
            attendance = round(random.uniform(85, 100), 1)
            study_hours = round(random.uniform(20, 30), 1)
            previous_grades = round(random.uniform(80, 100), 1)
            assignments = round(random.uniform(85, 100), 1)
            participation = random.choice([2, 3])
            
        elif category < 0.55:  # 35% Good students
            attendance = round(random.uniform(75, 90), 1)
            study_hours = round(random.uniform(15, 25), 1)
            previous_grades = round(random.uniform(70, 85), 1)
            assignments = round(random.uniform(75, 90), 1)
            participation = random.choice([2, 3])
            
        elif category < 0.85:  # 30% Average students
            attendance = round(random.uniform(65, 80), 1)
            study_hours = round(random.uniform(10, 20), 1)
            previous_grades = round(random.uniform(60, 75), 1)
            assignments = round(random.uniform(65, 80), 1)
            participation = random.choice([1, 2, 3])
            
        else:  # 15% Struggling students
            attendance = round(random.uniform(40, 70), 1)
            study_hours = round(random.uniform(5, 15), 1)
            previous_grades = round(random.uniform(40, 65), 1)
            assignments = round(random.uniform(50, 70), 1)
            participation = random.choice([1, 2])
        
        # Write to CSV
        f.write(f'{student_id},{attendance},{study_hours},{previous_grades},{assignments},{participation}\n')
        
        # Progress indicator
        if i % 1000 == 0:
            print(f"✓ Generated {i} students...")

print()
print("=" * 60)
print("✅ SUCCESS!")
print("=" * 60)
print(f"📁 File created: student_data_7000.csv")
print(f"📊 Total students: 7000")
print()
print("Dataset Distribution:")
print("  🌟 Excellent (80-100%): 1400 students (20%)")
print("  ✅ Good (70-85%):       2450 students (35%)")
print("  📊 Average (60-75%):    2100 students (30%)")
print("  ⚠️  Struggling (<60%):  1050 students (15%)")
print()
print("📤 Ready to upload to your application!")
print("=" * 60)