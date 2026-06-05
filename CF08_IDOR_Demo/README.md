# Demo CF08 - Broken Access Control / IDOR

## 1. Mục tiêu

Demo này minh họa lỗi **Broken Access Control / IDOR**.

Tình huống:
- Alice đăng nhập vào hệ thống.
- Alice được xem profile của mình tại `/profile_vuln?id=1`.
- Alice sửa URL thành `/profile_vuln?id=2`.
- Nếu hệ thống hiển thị thông tin của Bob thì có lỗi IDOR.

Demo có 2 bản:
- **Bản lỗi:** `/profile_vuln?id=...`
- **Bản đã vá:** `/profile_fixed?id=...`

## 2. Công nghệ sử dụng

- Python
- Flask
- Dữ liệu giả lưu trong code, không dùng dữ liệu thật.

## 3. Cài đặt

### Bước 1: Mở terminal tại thư mục project

```bash
cd idor_broken_access_control_demo
```

### Bước 2: Tạo môi trường ảo

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài thư viện

```bash
pip install -r requirements.txt
```

### Bước 4: Chạy app

```bash
python app.py
```

Sau đó mở trình duyệt:

```text
http://127.0.0.1:5000
```

## 4. Tài khoản demo

| Username | Password | Role | ID |
|---|---|---|---|
| alice | 123456 | user | 1 |
| bob | 123456 | user | 2 |
| admin | admin123 | admin | 3 |

## 5. Kịch bản demo bản lỗi IDOR

### Bước 1: Đăng nhập Alice

Vào:

```text
http://127.0.0.1:5000/login
```

Đăng nhập:

```text
username: alice
password: 123456
```

### Bước 2: Alice xem profile của mình

Vào:

```text
http://127.0.0.1:5000/profile_vuln?id=1
```

Kết quả: hệ thống hiển thị thông tin của Alice.

### Bước 3: Alice sửa URL thành id=2

Sửa URL thành:

```text
http://127.0.0.1:5000/profile_vuln?id=2
```

Kết quả: hệ thống hiển thị thông tin của Bob.

Đây là lỗi **IDOR**, vì Alice không phải chủ sở hữu tài nguyên của Bob nhưng vẫn xem được.

## 6. Nguyên nhân lỗi

Trong route `/profile_vuln`, backend chỉ kiểm tra người dùng đã đăng nhập hay chưa.

Code lỗi:

```python
redirect_response = login_required()
if redirect_response:
    return redirect_response

target_id = request.args.get("id", type=int)
target_user = USERS.get(target_id)
```

Vấn đề:
- Hệ thống nhận `id` từ URL.
- Hệ thống lấy dữ liệu theo `id`.
- Hệ thống không kiểm tra `current_user.id == target_id`.
- Hệ thống không kiểm tra role/permission.

Vì vậy, người dùng có thể thay đổi ID trên URL để xem dữ liệu người khác.

## 7. Kịch bản demo bản vá

### Bước 1: Vẫn đăng nhập Alice

### Bước 2: Truy cập bản đã vá với id=1

```text
http://127.0.0.1:5000/profile_fixed?id=1
```

Kết quả: Alice xem được profile của mình.

### Bước 3: Truy cập bản đã vá với id=2

```text
http://127.0.0.1:5000/profile_fixed?id=2
```

Kết quả: hệ thống trả về **403 - Bị từ chối truy cập**.

## 8. Code bản vá

```python
user = current_user()
is_owner = user["id"] == target_id
is_admin = user["role"] == "admin"

if not (is_owner or is_admin):
    return "403 Forbidden", 403
```

Ý nghĩa:
- User thường chỉ được xem dữ liệu của chính mình.
- Admin được xem dữ liệu người khác.
- Quyền phải được kiểm tra ở backend, không tin tưởng ID do client gửi lên.

## 9. Demo role admin

Đăng xuất Alice, đăng nhập admin:

```text
username: admin
password: admin123
```

Admin truy cập:

```text
http://127.0.0.1:5000/profile_fixed?id=1
http://127.0.0.1:5000/profile_fixed?id=2
```

Kết quả: admin được xem vì admin có quyền quản trị.

## 10. Demo API bằng Postman

Sau khi đăng nhập trên trình duyệt, có thể demo bằng URL:

Bản lỗi:

```text
GET http://127.0.0.1:5000/api/profile_vuln?id=2
```

Bản vá:

```text
GET http://127.0.0.1:5000/api/profile_fixed?id=2
```

Nếu dùng Postman riêng, cần gửi cookie session từ trình duyệt hoặc đăng nhập bằng Postman trước. Với bài thuyết trình, demo bằng trình duyệt là dễ nhất.

## 11. Nội dung nói khi thuyết trình

Authentication là xác thực, tức là kiểm tra bạn là ai. Ví dụ đăng nhập bằng username và password.

Authorization là phân quyền, tức là kiểm tra bạn được phép làm gì. Ví dụ Alice chỉ được xem profile của Alice, không được xem profile của Bob.

Trong bản lỗi, hệ thống có authentication nhưng thiếu authorization. Alice đã đăng nhập, nhưng backend không kiểm tra Alice có quyền truy cập tài nguyên `id=2` hay không.

Cách khắc phục là kiểm tra quyền ở backend:
- Kiểm tra chủ sở hữu tài nguyên.
- Kiểm tra role.
- Áp dụng nguyên tắc least privilege.
- Không tin tưởng ID do client gửi lên.
