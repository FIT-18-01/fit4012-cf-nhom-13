from flask import Flask, request, session, redirect, url_for, render_template_string, jsonify, abort

app = Flask(__name__)
app.secret_key = "demo-secret-key-only-for-local"

# DỮ LIỆU GIẢ - chỉ dùng để demo
USERS = {
    1: {
        "id": 1,
        "username": "alice",
        "password": "123456",
        "role": "user",
        "full_name": "Alice Nguyen",
        "email": "alice@example.com",
        "phone": "0901111111",
        "cccd": "001200000001",
        "address": "Ha Noi"
    },
    2: {
        "id": 2,
        "username": "bob",
        "password": "123456",
        "role": "user",
        "full_name": "Bob Tran",
        "email": "bob@example.com",
        "phone": "0902222222",
        "cccd": "001200000002",
        "address": "Da Nang"
    },
    3: {
        "id": 3,
        "username": "admin",
        "password": "admin123",
        "role": "admin",
        "full_name": "Admin System",
        "email": "admin@example.com",
        "phone": "0903333333",
        "cccd": "ADMIN-NO-REAL-DATA",
        "address": "System Office"
    }
}

def current_user():
    uid = session.get("user_id")
    if uid is None:
        return None
    return USERS.get(uid)

def find_user_by_username(username):
    for user in USERS.values():
        if user["username"] == username:
            return user
    return None

def login_required():
    if current_user() is None:
        return redirect(url_for("login"))
    return None

def safe_user_data(user):
    """Ẩn bớt dữ liệu nhạy cảm khi hiển thị demo."""
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "full_name": user["full_name"],
        "email": user["email"],
        "phone": user["phone"],
        "cccd": user["cccd"],
        "address": user["address"]
    }

BASE_HTML = """
<!doctype html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 30px auto; line-height: 1.5; }
        .box { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 14px 0; }
        .danger { background: #ffecec; border-color: #ffb3b3; }
        .safe { background: #ecfff1; border-color: #9ee2ad; }
        .info { background: #eef5ff; border-color: #b7d1ff; }
        code { background: #f2f2f2; padding: 2px 5px; border-radius: 4px; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; }
        td, th { border: 1px solid #ddd; padding: 8px; text-align: left; }
        a { margin-right: 10px; }
        button { padding: 7px 12px; }
        input { padding: 7px; margin: 5px 0; width: 250px; }
    </style>
</head>
<body>
    {{ body|safe }}
</body>
</html>
"""

def render_page(title, body):
    return render_template_string(BASE_HTML, title=title, body=body)

@app.route("/")
def index():
    user = current_user()
    if user:
        auth_html = f"""
        <p>Đang đăng nhập: <b>{user['username']}</b> - role: <b>{user['role']}</b></p>
        <a href="/logout">Đăng xuất</a>
        """
    else:
        auth_html = '<p>Bạn chưa đăng nhập. <a href="/login">Đăng nhập</a></p>'

    body = f"""
    <h1>Demo CF08 - Broken Access Control / IDOR</h1>
    <div class="box info">
        <b>Mục tiêu:</b> Minh họa lỗi hệ thống chỉ kiểm tra “đã đăng nhập” nhưng không kiểm tra người dùng hiện tại
        có quyền xem tài nguyên theo ID hay không.
    </div>
    {auth_html}

    <h2>Tài khoản demo</h2>
    <table>
        <tr><th>Username</th><th>Password</th><th>Role</th><th>ID</th></tr>
        <tr><td>alice</td><td>123456</td><td>user</td><td>1</td></tr>
        <tr><td>bob</td><td>123456</td><td>user</td><td>2</td></tr>
        <tr><td>admin</td><td>admin123</td><td>admin</td><td>3</td></tr>
    </table>

    <h2>Link demo</h2>
    <div class="box danger">
        <b>Bản lỗi IDOR:</b><br>
        <a href="/profile_vuln?id=1">/profile_vuln?id=1</a>
        <a href="/profile_vuln?id=2">/profile_vuln?id=2</a>
        <p>Đăng nhập Alice rồi đổi <code>id=1</code> thành <code>id=2</code> để xem dữ liệu Bob.</p>
    </div>

    <div class="box safe">
        <b>Bản đã vá:</b><br>
        <a href="/profile_fixed?id=1">/profile_fixed?id=1</a>
        <a href="/profile_fixed?id=2">/profile_fixed?id=2</a>
        <p>Đăng nhập Alice rồi truy cập <code>id=2</code> sẽ bị từ chối 403.</p>
    </div>

    <h2>API demo bằng Postman</h2>
    <p>Bản lỗi: <code>GET /api/profile_vuln?id=2</code></p>
    <p>Bản vá: <code>GET /api/profile_fixed?id=2</code></p>
    """
    return render_page("IDOR Demo", body)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = find_user_by_username(username)

        if user and user["password"] == password:
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        return render_page("Login failed", """
        <h1>Đăng nhập thất bại</h1>
        <p>Sai username hoặc password.</p>
        <a href="/login">Thử lại</a>
        """)

    body = """
    <h1>Đăng nhập demo</h1>
    <div class="box info">
        <p>Dùng tài khoản: <b>alice / 123456</b> để demo lỗi IDOR.</p>
    </div>
    <form method="post">
        <label>Username</label><br>
        <input name="username" placeholder="alice"><br>
        <label>Password</label><br>
        <input name="password" type="password" placeholder="123456"><br><br>
        <button type="submit">Đăng nhập</button>
    </form>
    <p><a href="/">Về trang chủ</a></p>
    """
    return render_page("Login", body)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def user_table(user):
    return f"""
    <table>
        <tr><th>Trường</th><th>Giá trị</th></tr>
        <tr><td>ID</td><td>{user['id']}</td></tr>
        <tr><td>Username</td><td>{user['username']}</td></tr>
        <tr><td>Role</td><td>{user['role']}</td></tr>
        <tr><td>Họ tên</td><td>{user['full_name']}</td></tr>
        <tr><td>Email</td><td>{user['email']}</td></tr>
        <tr><td>SĐT</td><td>{user['phone']}</td></tr>
        <tr><td>CCCD giả</td><td>{user['cccd']}</td></tr>
        <tr><td>Địa chỉ</td><td>{user['address']}</td></tr>
    </table>
    """

@app.route("/profile_vuln")
def profile_vuln():
    # Chỉ kiểm tra đã đăng nhập hay chưa
    # KHÔNG kiểm tra người hiện tại có phải chủ sở hữu của profile đó không
    redirect_response = login_required()
    if redirect_response:
        return redirect_response

    target_id = request.args.get("id", type=int)
    target_user = USERS.get(target_id)
    if not target_user:
        abort(404)

    user = current_user()
    body = f"""
    <h1>Bản lỗi: IDOR / Broken Access Control</h1>
    <div class="box danger">
        <b>Lỗi:</b> Hệ thống chỉ kiểm tra bạn đã đăng nhập là <code>{user['username']}</code>,
        nhưng không kiểm tra bạn có quyền xem <code>id={target_id}</code> hay không.
    </div>
    <p>URL hiện tại: <code>/profile_vuln?id={target_id}</code></p>
    {user_table(target_user)}
    <p>
        <a href="/">Trang chủ</a>
        <a href="/profile_vuln?id=1">Xem id=1</a>
        <a href="/profile_vuln?id=2">Xem id=2</a>
        <a href="/profile_fixed?id={target_id}">Thử bản vá với ID này</a>
    </p>
    """
    return render_page("Vulnerable Profile", body)

@app.route("/profile_fixed")
def profile_fixed():
    # Kiểm tra đã đăng nhập
    redirect_response = login_required()
    if redirect_response:
        return redirect_response

    target_id = request.args.get("id", type=int)
    target_user = USERS.get(target_id)
    if not target_user:
        abort(404)

    user = current_user()

    # BẢN VÁ:
    # 1. User thường chỉ được xem chính profile của mình
    # 2. Admin được phép xem profile người khác
    is_owner = user["id"] == target_id
    is_admin = user["role"] == "admin"

    if not (is_owner or is_admin):
        return render_page("403 Forbidden", f"""
        <h1>403 - Bị từ chối truy cập</h1>
        <div class="box safe">
            <b>Đã chặn thành công.</b><br>
            Người dùng hiện tại: <code>{user['username']}</code> - id=<code>{user['id']}</code><br>
            Đang cố truy cập tài nguyên của user id=<code>{target_id}</code>.<br>
            Backend đã kiểm tra owner/role nên không cho phép.
        </div>
        <p><a href="/">Trang chủ</a></p>
        """), 403

    body = f"""
    <h1>Bản vá: kiểm tra owner/role ở backend</h1>
    <div class="box safe">
        <b>Hợp lệ:</b> Bạn là chủ sở hữu tài nguyên hoặc là admin.
    </div>
    <p>URL hiện tại: <code>/profile_fixed?id={target_id}</code></p>
    {user_table(target_user)}
    <p>
        <a href="/">Trang chủ</a>
        <a href="/profile_fixed?id=1">Xem id=1</a>
        <a href="/profile_fixed?id=2">Xem id=2</a>
    </p>
    """
    return render_page("Fixed Profile", body)

@app.route("/api/profile_vuln")
def api_profile_vuln():
    redirect_response = login_required()
    if redirect_response:
        return jsonify({"error": "unauthenticated"}), 401

    target_id = request.args.get("id", type=int)
    target_user = USERS.get(target_id)
    if not target_user:
        return jsonify({"error": "not_found"}), 404

    # LỖI: trả về dữ liệu theo ID client gửi lên, không kiểm tra quyền
    return jsonify({
        "warning": "VULNERABLE: only checks login, not owner/role",
        "data": safe_user_data(target_user)
    })

@app.route("/api/profile_fixed")
def api_profile_fixed():
    redirect_response = login_required()
    if redirect_response:
        return jsonify({"error": "unauthenticated"}), 401

    target_id = request.args.get("id", type=int)
    target_user = USERS.get(target_id)
    if not target_user:
        return jsonify({"error": "not_found"}), 404

    user = current_user()
    is_owner = user["id"] == target_id
    is_admin = user["role"] == "admin"

    if not (is_owner or is_admin):
        return jsonify({
            "error": "forbidden",
            "message": "Bạn không có quyền truy cập tài nguyên này.",
            "current_user_id": user["id"],
            "target_user_id": target_id
        }), 403

    return jsonify({
        "message": "OK: owner/role check passed",
        "data": safe_user_data(target_user)
    })

@app.errorhandler(404)
def not_found(e):
    return render_page("404", """
    <h1>404 - Không tìm thấy</h1>
    <p>ID hoặc đường dẫn không tồn tại.</p>
    <p><a href="/">Trang chủ</a></p>
    """), 404

if __name__ == "__main__":
    app.run(debug=True)
