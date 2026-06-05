# Threat Model - CF08 Broken Access Control / IDOR

## 1. Tài sản cần bảo vệ

Các tài sản trong hệ thống demo:

- Thông tin cá nhân người dùng.
- Email, số điện thoại.
- CCCD giả.
- Địa chỉ.
- Session đăng nhập.
- Quyền truy cập theo user/role.

## 2. Tác nhân

| Tác nhân | Mô tả |
|---|---|
| User thường | Alice, Bob |
| Admin | Người có quyền quản trị |
| Attacker | Người dùng đã đăng nhập nhưng cố truy cập dữ liệu người khác |

## 3. Luồng nghiệp vụ hợp lệ

- Alice đăng nhập.
- Alice chỉ được xem profile của Alice.
- Bob đăng nhập.
- Bob chỉ được xem profile của Bob.
- Admin đăng nhập.
- Admin được xem profile người dùng để quản trị.

## 4. Lỗ hổng

Tên lỗ hổng:

```text
Broken Access Control / IDOR
```

Mô tả:

Hệ thống nhận ID tài nguyên từ URL/API như:

```text
/profile?id=2
```

nhưng backend chỉ kiểm tra người dùng đã đăng nhập, không kiểm tra người dùng hiện tại có quyền truy cập tài nguyên đó hay không.

## 5. Nguyên nhân

- Tin tưởng ID do client gửi lên.
- Thiếu kiểm tra owner ở backend.
- Thiếu kiểm tra role/permission.
- Nhầm lẫn giữa authentication và authorization.

## 6. Kịch bản tấn công

1. Alice đăng nhập.
2. Alice truy cập `/profile_vuln?id=1`.
3. Alice sửa URL thành `/profile_vuln?id=2`.
4. Hệ thống trả về dữ liệu của Bob.
5. Alice xem được dữ liệu không thuộc quyền của mình.

## 7. Tác động

| Tác động | Mức độ |
|---|---|
| Lộ thông tin cá nhân | Cao |
| Vi phạm quyền riêng tư | Cao |
| Mất uy tín hệ thống | Cao |
| Có thể dẫn tới sửa/xóa dữ liệu trái phép nếu API cho phép update/delete | Cao |
| Vi phạm chính sách bảo mật dữ liệu | Cao |

## 8. Kiểm soát / Biện pháp khắc phục

### 8.1. Kiểm tra owner

User thường chỉ được truy cập dữ liệu thuộc về chính user đó.

Ví dụ:

```python
if current_user.id != target_user.id:
    deny_access()
```

### 8.2. Kiểm tra role

Admin có quyền cao hơn user thường.

Ví dụ:

```python
if current_user.id == target_id or current_user.role == "admin":
    allow_access()
else:
    deny_access()
```

### 8.3. Không tin tưởng dữ liệu từ client

ID trong URL, body request, form, header đều có thể bị thay đổi.

Backend phải tự kiểm tra quyền.

### 8.4. Áp dụng least privilege

Người dùng chỉ được cấp quyền tối thiểu cần thiết.

Ví dụ:
- Alice chỉ xem/sửa dữ liệu Alice.
- Bob chỉ xem/sửa dữ liệu Bob.
- Admin mới được xem nhiều user.

### 8.5. Ghi log truy cập bất thường

Có thể ghi log khi user cố truy cập ID không thuộc quyền.

Ví dụ:
- user_id hiện tại
- target_id
- thời gian
- IP
- endpoint

## 9. Bản vá trong demo

Bản lỗi:

```text
/profile_vuln?id=2
```

Chỉ kiểm tra đăng nhập.

Bản vá:

```text
/profile_fixed?id=2
```

Kiểm tra:
- Người dùng hiện tại có phải chủ sở hữu không?
- Hoặc người dùng hiện tại có role admin không?

Nếu không hợp lệ, trả về:

```text
403 Forbidden
```

## 10. Kết luận

Lỗi IDOR xảy ra khi hệ thống để người dùng truy cập tài nguyên bằng ID mà không kiểm tra quyền ở backend.

Cách phòng tránh quan trọng nhất là luôn kiểm tra authorization cho từng request, đặc biệt với các chức năng xem, sửa, xóa dữ liệu theo ID.
