from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Dùng secret_key để quản lý session

# Cấu hình kết nối database
DB_CONFIG = {
    'dbname': 'students',
    'host': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'Tinny987654321'
}

# Hàm kết nối cơ sở dữ liệu
def get_db_connection(username, password):
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        return conn
    except Exception as e:
        print("Connection failed:", e)
        return None

@app.route('/', methods=['GET', 'POST'])
def login():        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'thanhtrung' and password == '1001': 
            session['username'] = username
            session['password'] = password
            return redirect(url_for('student_management'))
        else:
            flash("Đăng nhập thất bại. Vui lòng thử lại!", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Kết nối cơ sở dữ liệu
        conn = get_db_connection(session.get('username'), session.get('password'))
        if conn is None:
            flash("Không thể kết nối tới cơ sở dữ liệu", "danger")
            return redirect(url_for('login'))

        cur = conn.cursor()
        try:
            # Kiểm tra xem username đã tồn tại chưa
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cur.fetchone()
            if existing_user:
                flash("Tên đăng nhập đã tồn tại!", "danger")
            else:
                # Thêm người dùng mới vào bảng
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                flash("Đăng ký thành công! Bạn có thể đăng nhập ngay.", "success")
                return redirect(url_for('login'))

        except Exception as e:
            flash(f"Đã xảy ra lỗi: {str(e)}", "danger")
        finally:
            cur.close()
            conn.close()
    
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        
        # Kiểm tra nếu người dùng có trong hệ thống
        conn = get_db_connection(session.get('username'), session.get('password'))
        if conn is None:
            flash("Không thể kết nối tới cơ sở dữ liệu", "danger")
            return redirect(url_for('login'))

        cur = conn.cursor()
        try:
            # Kiểm tra nếu username tồn tại
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

            if user:
                # Nếu người dùng tồn tại, bạn có thể gửi email reset mật khẩu
                flash("Nếu tài khoản tồn tại, chúng tôi đã gửi email hướng dẫn đến bạn.", "info")
            else:
                flash("Tài khoản không tồn tại!", "danger")
        
        except Exception as e:
            flash(f"Đã xảy ra lỗi: {str(e)}", "danger")
        finally:
            cur.close()
            conn.close()
    
    return render_template('forgot_password.html')



@app.route('/student_management', methods=['GET', 'POST'])
def student_management():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection(session['username'], session['password'])
    if conn is None:
        flash("Không thể kết nối tới cơ sở dữ liệu", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        major = request.form.get('major')
        action = request.form.get('action')

        cur = conn.cursor()
        try:
            if action == 'add':
                if name:  # Kiểm tra nếu tên không rỗng
                    cur.execute(
                        "INSERT INTO students (name, age, gender, major) VALUES (%s, %s, %s, %s)",
                        (name, age, gender, major)
                    )
                    flash("Sinh viên đã được thêm!", "success")
                else:
                    flash("Tên sinh viên không được để trống!", "danger")

            elif action == 'update':
                if student_id and name:  # Kiểm tra nếu ID và tên không rỗng
                    cur.execute(
                        "UPDATE students SET name=%s, age=%s, gender=%s, major=%s WHERE id=%s",
                        (name, age, gender, major, student_id)
                    )
                    flash("Thông tin sinh viên đã được cập nhật!", "success")
                else:
                    flash("ID sinh viên và tên không được để trống!", "danger")

            elif action == 'delete':
                if student_id:  # Kiểm tra nếu ID không rỗng
                    cur.execute("DELETE FROM students WHERE id=%s", (student_id,))
                    flash("Sinh viên đã được xóa!", "success")
                else:
                    flash("ID sinh viên không được để trống!", "danger")

            conn.commit()
        except Exception as e:
            conn.rollback()  # Quay lại nếu có lỗi
            flash(f"Đã xảy ra lỗi: {str(e)}", "danger")
        finally:
            cur.close()

    # Load danh sách sinh viên
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('student_management.html', students=students)

@app.route('/logout')
def logout():
    session.clear()
    flash("Đã đăng xuất!", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
