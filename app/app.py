import os
from flask import Flask, jsonify, request, render_template_string
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

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                class_name VARCHAR(100) NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_code VARCHAR(20) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                class_id INT,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
            );
        """)
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
    except Exception as e:
        print(f"Lỗi DB: {e}")

# HTML Template khớp 100% giao diện Bootstrap Blue Navbar
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hệ Thống Quản Lý Sinh Viên</title>
    <style>
        :root { --blue-primary: #0d6efd; --blue-hover: #0b5ed7; --bg-gray: #f4f6f9; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
        body { background-color: var(--bg-gray); color: #212529; }
        
        /* Navbar */
        .navbar { background-color: #007bff; padding: 12px 10%; display: flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .navbar-brand { color: white; text-decoration: none; font-weight: 700; font-size: 18px; margin-right: 30px; display: flex; align-items: center; gap: 8px; }
        .nav-links { display: flex; gap: 15px; }
        .nav-link { color: rgba(255, 255, 255, 0.85); text-decoration: none; font-weight: 600; font-size: 14px; padding: 6px 12px; border-radius: 4px; transition: 0.2s; display: flex; align-items: center; gap: 6px; }
        .nav-link:hover, .nav-link.active { color: white; background-color: rgba(255, 255, 255, 0.15); }
        
        /* Layout Container */
        .container { max-width: 1200px; margin: 30px auto; padding: 0 15px; display: grid; grid-template-columns: 380px 1fr; gap: 25px; }
        
        /* Card UI */
        .card { background: white; border-radius: 6px; border: 1px solid #e3e6f0; box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.05); padding: 20px; }
        .card-title { font-size: 16px; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; color: #007bff; }
        .card-title.black { color: #212529; }
        
        /* Forms */
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; color: #495057; }
        .form-control { width: 100%; padding: 10px 12px; border: 1px solid #ced4da; border-radius: 5px; font-size: 14px; color: #495057; transition: border-color 0.15s ease-in-out; }
        .form-control:focus { border-color: #80bdff; outline: 0; box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25); }
        select.form-control { background-color: white; }
        
        /* Buttons */
        .btn-blue { width: 100%; background-color: #007bff; color: white; border: none; padding: 10px; border-radius: 5px; font-weight: 600; font-size: 14px; cursor: pointer; transition: 0.2s; display: flex; justify-content: center; align-items: center; gap: 6px; }
        .btn-blue:hover { background-color: #0056b3; }
        .btn-danger { background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; font-weight: 600; }
        .btn-danger:hover { background-color: #bd2130; }
        
        /* Table */
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 12px; font-size: 14px; font-weight: 700; color: #212529; border-bottom: 2px solid #dee2e6; }
        td { padding: 12px; font-size: 14px; border-bottom: 1px solid #dee2e6; color: #495057; vertical-align: middle; }
        .empty-row { text-align: center; color: #6c757d; padding: 30px 0; }
        .code-tag { background: #e9ecef; padding: 3px 6px; border-radius: 4px; font-family: monospace; font-size: 13px; color: #333; }
    </style>
</head>
<body>

    <nav class="navbar">
        <a href="/classes" class="navbar-brand">🎓 QUẢN LÝ SINH VIÊN</a>
        <div class="nav-links">
            <a href="/classes" class="nav-link {% if active_page == 'classes' %}active{% endif %}">🏢 Quản Lý Lớp</a>
            <a href="/students" class="nav-link {% if active_page == 'students' %}active{% endif %}">👥 Quản Lý Sinh Viên</a>
            <a href="/grades" class="nav-link {% if active_page == 'grades' %}active{% endif %}">⭐ Quản Lý Điểm Số</a>
        </div>
    </nav>

    <div class="container">
        {{ content | safe }}
    </div>

</body>
</html>
"""

# ================= 1. TRANG QUẢN LÝ LỚP =================
CLASSES_HTML = """
<div class="card">
    <div class="card-title">📝 Thêm Lớp Học Mới</div>
    <form id="formAddClass">
        <div class="form-group">
            <label class="form-label">Tên Lớp Học</label>
            <input type="text" id="class_name" class="form-control" placeholder="VD: CNTT K18A" required>
        </div>
        <button type="submit" class="btn-blue">💾 Lưu Lớp Học</button>
    </form>
</div>

<div class="card">
    <div class="card-title black">🏢 Danh Sách Lớp Học</div>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Tên Lớp Học</th>
                <th>Thao Tác</th>
            </tr>
        </thead>
        <tbody id="tableBody">
            <tr><td colspan="3" class="empty-row">Đang tải dữ liệu...</td></tr>
        </tbody>
    </table>
</div>

<script>
    async function loadData() {
        const res = await fetch('/api/classes');
        const data = await res.json();
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';
        if(data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="empty-row">Chưa có dữ liệu lớp học.</td></tr>';
            return;
        }
        data.forEach(item => {
            tbody.innerHTML += `
                <tr>
                    <td>${item.id}</td>
                    <td><strong>${item.class_name}</strong></td>
                    <td><button class="btn-danger" onclick="deleteItem(${item.id})">Xóa</button></td>
                </tr>
            `;
        });
    }

    document.getElementById('formAddClass').addEventListener('submit', async (e) => {
        e.preventDefault();
        await fetch('/api/classes', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ class_name: document.getElementById('class_name').value })
        });
        document.getElementById('class_name').value = '';
        loadData();
    });

    async function deleteItem(id) {
        if(confirm('Bạn có chắc chắn muốn xóa lớp này?')) {
            await fetch('/api/classes/' + id, { method: 'DELETE' });
            loadData();
        }
    }
    loadData();
</script>
"""

# ================= 2. TRANG QUẢN LÝ SINH VIÊN =================
STUDENTS_HTML = """
<div class="card">
    <div class="card-title">📝 Thêm Sinh Viên Mới</div>
    <form id="formAddStudent">
        <div class="form-group">
            <label class="form-label">Mã Sinh Viên</label>
            <input type="text" id="student_code" class="form-control" placeholder="VD: SV202601" required>
        </div>
        <div class="form-group">
            <label class="form-label">Họ và Tên</label>
            <input type="text" id="full_name" class="form-control" placeholder="VD: Nguyễn Văn A" required>
        </div>
        <div class="form-group">
            <label class="form-label">Chọn Lớp Học</label>
            <select id="class_id" class="form-control">
                <option value="">-- Chọn lớp học --</option>
            </select>
        </div>
        <button type="submit" class="btn-blue">💾 Lưu Sinh Viên</button>
    </form>
</div>

<div class="card">
    <div class="card-title black">👥 Danh Sách Sinh Viên</div>
    <table>
        <thead>
            <tr>
                <th>Mã SV</th>
                <th>Họ và Tên</th>
                <th>Lớp</th>
                <th>Thao Tác</th>
            </tr>
        </thead>
        <tbody id="tableBody">
            <tr><td colspan="4" class="empty-row">Đang tải dữ liệu...</td></tr>
        </tbody>
    </table>
</div>

<script>
    async function loadClassesSelect() {
        const res = await fetch('/api/classes');
        const data = await res.json();
        const select = document.getElementById('class_id');
        select.innerHTML = '<option value="">-- Chọn lớp học --</option>';
        data.forEach(c => { select.innerHTML += `<option value="${c.id}">${c.class_name}</option>`; });
    }

    async function loadData() {
        const res = await fetch('/api/students');
        const data = await res.json();
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';
        if(data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-row">Chưa có dữ liệu sinh viên.</td></tr>';
            return;
        }
        data.forEach(item => {
            tbody.innerHTML += `
                <tr>
                    <td><span class="code-tag">${item.student_code}</span></td>
                    <td><strong>${item.full_name}</strong></td>
                    <td>${item.class_name || 'Chưa gán'}</td>
                    <td><button class="btn-danger" onclick="deleteItem(${item.id})">Xóa</button></td>
                </tr>
            `;
        });
    }

    document.getElementById('formAddStudent').addEventListener('submit', async (e) => {
        e.preventDefault();
        await fetch('/api/students', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                student_code: document.getElementById('student_code').value,
                full_name: document.getElementById('full_name').value,
                class_id: document.getElementById('class_id').value || null
            })
        });
        document.getElementById('student_code').value = '';
        document.getElementById('full_name').value = '';
        loadData();
    });

    async function deleteItem(id) {
        if(confirm('Bạn có chắc muốn xóa sinh viên này?')) {
            await fetch('/api/students/' + id, { method: 'DELETE' });
            loadData();
        }
    }
    loadClassesSelect();
    loadData();
</script>
"""

# ================= 3. TRANG QUẢN LÝ ĐIỂM SỐ =================
GRADES_HTML = """
<div class="card">
    <div class="card-title">📝 Nhập Điểm Số</div>
    <form id="formAddGrade">
        <div class="form-group">
            <label class="form-label">Chọn Sinh Viên</label>
            <select id="student_id" class="form-control" required>
                <option value="">-- Chọn sinh viên --</option>
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Tên Môn Học</label>
            <input type="text" id="subject_name" class="form-control" placeholder="VD: Triển khai hệ thống" required>
        </div>
        <div class="form-group">
            <label class="form-label">Điểm Số (Hệ 10)</label>
            <input type="number" step="0.1" min="0" max="10" id="score" class="form-control" placeholder="VD: 8.5" required>
        </div>
        <button type="submit" class="btn-blue">💾 Lưu Điểm Số</button>
    </form>
</div>

<div class="card">
    <div class="card-title black">📋 Bảng Điểm Tổng Hợp</div>
    <table>
        <thead>
            <tr>
                <th>Mã SV</th>
                <th>Họ và Tên</th>
                <th>Môn Học</th>
                <th>Điểm Số</th>
                <th>Thao Tác</th>
            </tr>
        </thead>
        <tbody id="tableBody">
            <tr><td colspan="5" class="empty-row">Chưa có dữ liệu điểm số.</td></tr>
        </tbody>
    </table>
</div>

<script>
    async function loadStudentsSelect() {
        const res = await fetch('/api/students');
        const data = await res.json();
        const select = document.getElementById('student_id');
        select.innerHTML = '<option value="">-- Chọn sinh viên --</option>';
        data.forEach(s => { select.innerHTML += `<option value="${s.id}">${s.student_code} - ${s.full_name}</option>`; });
    }

    async function loadData() {
        const res = await fetch('/api/grades');
        const data = await res.json();
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';
        if(data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-row">Chưa có dữ liệu điểm số.</td></tr>';
            return;
        }
        data.forEach(item => {
            tbody.innerHTML += `
                <tr>
                    <td><span class="code-tag">${item.student_code}</span></td>
                    <td><strong>${item.full_name}</strong></td>
                    <td>${item.subject_name}</td>
                    <td><strong style="color: #28a745;">${item.score}</strong></td>
                    <td><button class="btn-danger" onclick="deleteItem(${item.id})">Xóa</button></td>
                </tr>
            `;
        });
    }

    document.getElementById('formAddGrade').addEventListener('submit', async (e) => {
        e.preventDefault();
        await fetch('/api/grades', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                student_id: document.getElementById('student_id').value,
                subject_name: document.getElementById('subject_name').value,
                score: parseFloat(document.getElementById('score').value)
            })
        });
        document.getElementById('subject_name').value = '';
        document.getElementById('score').value = '';
        loadData();
    });

    async function deleteItem(id) {
        if(confirm('Xóa điểm môn học này?')) {
            await fetch('/api/grades/' + id, { method: 'DELETE' });
            loadData();
        }
    }
    loadStudentsSelect();
    loadData();
</script>
"""

# ================= ROUTES DẪN HƯỚNG TRANG =================

@app.route('/')
@app.route('/classes')
def page_classes():
    REQUEST_COUNT.inc()
    return render_template_string(BASE_TEMPLATE, active_page='classes', content=CLASSES_HTML)

@app.route('/students')
def page_students():
    REQUEST_COUNT.inc()
    return render_template_string(BASE_TEMPLATE, active_page='students', content=STUDENTS_HTML)

@app.route('/grades')
def page_grades():
    REQUEST_COUNT.inc()
    return render_template_string(BASE_TEMPLATE, active_page='grades', content=GRADES_HTML)

# ================= API ENDPOINTS =================

@app.route('/api/classes', methods=['GET', 'POST'])
def api_classes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute("INSERT INTO classes (class_name) VALUES (%s);", (request.json.get('class_name'),))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'OK'}), 201
    cursor.execute("SELECT * FROM classes;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/api/classes/<int:id>', methods=['DELETE'])
def api_delete_class(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM classes WHERE id = %s;", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'OK'})

@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.json
        cursor.execute("INSERT INTO students (student_code, full_name, class_id) VALUES (%s, %s, %s);",
                       (data.get('student_code'), data.get('full_name'), data.get('class_id')))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'OK'}), 201
    cursor.execute("SELECT s.id, s.student_code, s.full_name, c.class_name FROM students s LEFT JOIN classes c ON s.class_id = c.id;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/api/students/<int:id>', methods=['DELETE'])
def api_delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s;", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'OK'})

@app.route('/api/grades', methods=['GET', 'POST'])
def api_grades():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.json
        cursor.execute("INSERT INTO grades (student_id, subject_name, score) VALUES (%s, %s, %s);",
                       (data.get('student_id'), data.get('subject_name'), data.get('score')))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'OK'}), 201
    cursor.execute("SELECT g.id, s.student_code, s.full_name, g.subject_name, g.score FROM grades g JOIN students s ON g.student_id = s.id;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/api/grades/<int:id>', methods=['DELETE'])
def api_delete_grade(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grades WHERE id = %s;", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'OK'})

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print(f"Chờ DB: {e}")
    app.run(host='0.0.0.0', port=5000)
