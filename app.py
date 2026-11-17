from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
import csv

app = Flask(__name__)

FILE_NAME = "students.csv"
SUBJECTS = ["Python", "DBMS", "Java", "Web", "AI"]
COLUMNS = [
    "Roll No", "Name", "Python", "DBMS", "Java", "Web", "AI",
    "Classes Held", "Classes Attended", "Total", "Average",
    "Percentage", "Grade", "Attendance"
]

def create_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(COLUMNS)

def load_data():
    create_file()
    try:
        df = pd.read_csv(FILE_NAME)
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

def calculate_grade(percentage):
    if percentage >= 90: return "A+"
    elif percentage >= 80: return "A"
    elif percentage >= 70: return "B+"
    elif percentage >= 60: return "B"
    elif percentage >= 50: return "C"
    elif percentage >= 40: return "D"
    else: return "F"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/students', methods=['GET'])
def get_students():
    df = load_data()
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/add_student', methods=['POST'])
def add_student():
    data = request.json
    df = load_data()

    roll_no = int(data['roll_no'])
    
    if not df.empty and "Roll No" in df.columns:
        existing_rolls = pd.to_numeric(df["Roll No"], errors='coerce').fillna(-1).astype(int).tolist()
        if roll_no in existing_rolls:
            return jsonify({"success": False, "message": "Roll number already exists!"})

    marks = [float(data['python']), float(data['dbms']), float(data['java']), float(data['web']), float(data['ai'])]
    classes_held = int(data['classes_held'])
    classes_attended = int(data['classes_attended'])

    marks_array = np.array(marks)
    total = float(np.sum(marks_array))
    average = float(np.mean(marks_array))
    percentage = (total / 500) * 100
    attendance = (classes_attended / classes_held) * 100
    grade = calculate_grade(percentage)

    new_student = {
        "Roll No": roll_no,
        "Name": data['name'],
        "Python": marks[0],
        "DBMS": marks[1],
        "Java": marks[2],
        "Web": marks[3],
        "AI": marks[4],
        "Classes Held": classes_held,
        "Classes Attended": classes_attended,
        "Total": round(total, 2),
        "Average": round(average, 2),
        "Percentage": round(percentage, 2),
        "Grade": grade,
        "Attendance": round(attendance, 2)
    }

    df = pd.concat([df, pd.DataFrame([new_student])], ignore_index=True)
    save_data(df)
    return jsonify({"success": True, "message": "Student added successfully!"})

@app.route('/api/analysis', methods=['GET'])
def data_analysis():
    df = load_data()
    if df.empty:
        return jsonify({"has_data": False})

    percentages = pd.to_numeric(df["Percentage"], errors='coerce').to_numpy()
    topper_index = df["Percentage"].astype(float).idxmax()
    
    analysis = {
        "has_data": True,
        "total_students": len(df),
        "class_avg": round(float(np.mean(percentages)), 2),
        "highest_pct": round(float(np.max(percentages)), 2),
        "lowest_pct": round(float(np.min(percentages)), 2),
        "topper": df.loc[topper_index, "Name"],
        "passed": int(len(df[df["Percentage"].astype(float) >= 40])),
        "failed": int(len(df[df["Percentage"].astype(float) < 40]))
    }
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True)