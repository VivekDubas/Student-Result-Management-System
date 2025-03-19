from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"  # Required for session handling

# Connect to MySQL Database
db = pymysql.connect(
    host="localhost",
    user="root",   # Change this to your MySQL username
    password="MyDvK@2211Sql",   # Change this if you have a MySQL password
    database="student_result_db"
)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template('home1.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json()  # Handle JSON request
        if data:
            admin_id = data.get('admin_id')
            password = data.get('admin_password')
        else:
            admin_id = request.form['admin_id']  # Handle Form Data
            password = request.form['admin_password']

        cursor.execute("SELECT name FROM admin WHERE id=%s AND password=%s", (admin_id, password))
        admin = cursor.fetchone()

        if admin:
            session['admin_id'] = admin_id  # Store admin ID
            session['admin_name'] = admin[0]  # Store admin name
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Invalid credentials"}

    return render_template("admin_login.html")



@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        data = request.get_json()  # Handles JSON request
        if data:
            student_id = data.get('student_id')
            password = data.get('student_password')
        else:
            student_id = request.form['student_id']  # Handles Form Data
            password = request.form['student_password']

        cursor.execute("SELECT name FROM students WHERE id=%s AND password=%s", (student_id, password))
        student = cursor.fetchone()

        if student:
            session['student_id'] = student_id  # Store student ID in session
            session['student_name'] = student[0]  # Store student name
            return {"status": "success"}  # Send success response
        else:
            return {"status": "error", "message": "Invalid credentials"}

    return render_template("student_login.html")


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' in session:
        admin_name = session.get('admin_name', 'Admin')  # Default to 'Admin' if no name found
        return render_template("admin_dashboard.html", admin_name=admin_name)
    else:
        return redirect(url_for('admin_login'))


@app.route('/student_dashboard')
def student_dashboard():
    if 'student_id' in session:
        student_id = session['student_id']

        # Fetch student details from the database
        cursor.execute("SELECT name, father_name, mother_name, class, section FROM students WHERE id=%s", (student_id,))
        student = cursor.fetchone()

        # Fetch student marks from the database
        cursor.execute("SELECT subject1, subject2, subject3, subject4, subject5, subject6 FROM student_marks WHERE student_id=%s", (student_id,))
        marks = cursor.fetchone()

        if student and marks:
            student_data = {
                "name": student[0],
                "father_name": student[1],
                "mother_name": student[2],
                "class": student[3],
                "section": student[4],
                "marks": marks  # Storing marks in student_data
            }
            return render_template("student_dashboard.html", student_data=student_data)
        else:
            return "Student not found or marks not available", 404

    return redirect(url_for('student_login'))



@app.route('/student_details1', methods=['GET','POST'])
def student_details1():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template("StudentDetails1.html")

@app.route('/message_teacher', methods=['GET','POST'])
def message_teacher():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template("messageTeacher.html")
    
@app.route('/message_student')
def message_student():
    return render_template("messageStudent.html")  # Make sure this file exists


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/add_marks1', methods=['GET', 'POST'])
def add_marks1():
    if request.method == 'POST':
        roll_number = request.form.get('roll_number')  # Use .get() to avoid KeyError
        if not roll_number:
            return "Roll number is required", 400  # Return an error message if empty

        session['roll_number'] = roll_number  # Store roll number in session
        return redirect(url_for('add_marks2'))  # Redirect to AddMarks2

    return render_template("AddMarks1.html")


@app.route('/add_marks3')
def add_marks3():
    return render_template("AddMarks3.html")

@app.route('/add_marks2', methods=['GET', 'POST'])
def add_marks2():
    if 'roll_number' not in session:
        return redirect(url_for('add_marks1'))  # Redirect if no roll number found

    roll_number = session['roll_number']  # Retrieve roll number from session

    if request.method == 'POST':
        subject1 = request.form['subject1']
        subject2 = request.form['subject2']
        subject3 = request.form['subject3']
        subject4 = request.form['subject4']
        subject5 = request.form['subject5']
        subject6 = request.form['subject6']

        # Check if the student already has marks
        cursor.execute("SELECT * FROM student_marks WHERE roll_number = %s", (roll_number,))
        existing = cursor.fetchone()

        if existing:
            # Update existing marks
            cursor.execute("""
                UPDATE student_marks SET 
                subject1=%s, subject2=%s, subject3=%s, 
                subject4=%s, subject5=%s, subject6=%s
                WHERE roll_number=%s
            """, (subject1, subject2, subject3, subject4, subject5, subject6, roll_number))
        else:
            # Insert new marks
            cursor.execute("""
                INSERT INTO student_marks (roll_number, subject1, subject2, subject3, subject4, subject5, subject6)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (roll_number, subject1, subject2, subject3, subject4, subject5, subject6))

        db.commit()
        session.pop('roll_number', None)  # Clear roll number from session
        
        # Redirect to AddMarks3.html after successful submission
        return redirect(url_for('add_marks3'))

    return render_template("AddMarks2.html")






if __name__ == '__main__':
    app.run(debug=True)

