import os
from flask import Flask, jsonify, request
import mysql.connector
from prometheus_client import Counter, generate_latest

app = Flask(__name__)
REQUEST_COUNT = Counter('flask_app_requests_total', 'Total app requests')

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'db'),
        user=os.getenv('MYSQL_USER', 'student_user'),
        password=os.getenv('MYSQL_PASSWORD', 'SecurePass_123!'),
        database=os.getenv('MYSQL_DATABASE', 'student_db')
    )

# Hàm khởi tạo bảng dữ liệu tự động nếu chưa có
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Bảng Lớp học
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                class_name VARCHAR(100) NOT NULL
            );
        """)
        
        # Bảng Sinh viên
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_code VARCHAR(20) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                class_id INT,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
            );
        """)
        
        # Bảng Điểm số
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                subject_name VARCHAR(100) NOT NULL,
                score FLOAT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Khởi tạo cơ sở dữ liệu thành công!")
    except Exception as e:
        print(f"Lỗi khởi tạo DB: {e}")

# ==================== 1. QUẢN LÝ LỚP HỌC (CLASSES) ====================

@app.route('/api/classes', methods=['GET'])
def get_classes():
    REQUEST_COUNT.inc()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM classes;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data), 200

@app.route('/api/classes', methods=['POST'])
def create_class():
    REQUEST_COUNT.inc()
    data = request.json
    class_name = data.get('class_name')
    if not class_name:
        return jsonify({'error': 'Thiếu class_name'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO classes (class_name) VALUES (%s);", (class_name,))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'message': 'Tạo lớp thành công', 'id': new_id}), 201

@app.route('/api/classes/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    REQUEST_COUNT.inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM classes WHERE id = %s;", (class_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': f'Đã xóa lớp {class_id}'}), 200


# ==================== 2. QUẢN LÝ HỌC SINH (STUDENTS) ====================

@app.route('/api/students', methods=['GET'])
def get_students():
    REQUEST_COUNT.inc()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT s.id, s.student_code, s.full_name, c.class_name 
        FROM students s 
        LEFT JOIN classes c ON s.class_id = c.id;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data), 200

@app.route('/api/students', methods=['POST'])
def create_student():
    REQUEST_COUNT.inc()
    data = request.json
    student_code = data.get('student_code')
    full_name = data.get('full_name')
    class_id = data.get('class_id')
    
    if not student_code or not full_name:
        return jsonify({'error': 'Thiếu thông tin bắt buộc (student_code, full_name)'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (student_code, full_name, class_id) VALUES (%s, %s, %s);",
            (student_code, full_name, class_id)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'message': 'Thêm sinh viên thành công', 'id': new_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    REQUEST_COUNT.inc()
    data = request.json
    full_name = data.get('full_name')
    class_id = data.get('class_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET full_name = %s, class_id = %s WHERE id = %s;",
        (full_name, class_id, student_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': f'Cập nhật sinh viên {student_id} thành công'}), 200

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    REQUEST_COUNT.inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s;", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': f'Đã xóa sinh viên {student_id}'}), 200


# ==================== 3. QUẢN LÝ ĐIỂM SỐ (GRADES) ====================

@app.route('/api/grades', methods=['GET'])
def get_grades():
    REQUEST_COUNT.inc()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT g.id, s.student_code, s.full_name, g.subject_name, g.score 
        FROM grades g 
        JOIN students s ON g.student_id = s.id;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data), 200

@app.route('/api/grades', methods=['POST'])
def add_grade():
    REQUEST_COUNT.inc()
    data = request.json
    student_id = data.get('student_id')
    subject_name = data.get('subject_name')
    score = data.get('score')
    
    if not all([student_id, subject_name, score is not None]):
        return jsonify({'error': 'Thiếu thông tin điểm số'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO grades (student_id, subject_name, score) VALUES (%s, %s, %s);",
        (student_id, subject_name, score)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'message': 'Thêm điểm thành công', 'id': new_id}), 201


# ==================== 4. SYSTEM & METRICS ====================

@app.route('/')
def index():
    REQUEST_COUNT.inc()
    return "<h1>Hệ Thống Quản Lý Sinh Viên</h1><p>API CRUD đã sẵn sàng!</p>"

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    # Gọi hàm khởi tạo DB khi app bắt đầu
    try:
        init_db()
    except Exception as e:
        print(f"Chờ DB khởi động: {e}")
    app.run(host='0.0.0.0', port=5000)
