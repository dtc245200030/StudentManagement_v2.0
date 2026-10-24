# 🎓 Student Management System (SMS)
> **Đồ án môn Triển khai & Quản trị Phần mềm**

Hệ thống Quản lý Sinh viên được đóng gói hoàn chỉnh bằng **Docker Compose**, tích hợp **Nginx Reverse Proxy** (SSL/TLS), giám sát **Prometheus / Grafana**, thu thập log tập trung với **Loki / Promtail** và áp dụng các giải pháp **Hardening** bảo mật nâng cao.

---

## 🛠 Công Nghệ Sử Dụng

| Tầng / Thành phần | Công nghệ |
| :--- | :--- |
| **Frontend / Backend** | Flask (Python) |
| **Database & Management** | MySQL 8.0, phpMyAdmin |
| **Reverse Proxy & Security** | Nginx (HTTPS Self-signed & Security Headers) |
| **Monitoring** | Prometheus, Grafana, cAdvisor |
| **Logging** | Grafana Loki, Promtail |
| **Containerization** | Docker, Docker Compose |

---

## 🔒 Các Biện Pháp Hardening Đã Áp Dụng

- **Non-root Container:** Chạy ứng dụng Flask dưới dạng user hạn chế quyền (`appuser`).
- **Network Isolation:** Phân chia rõ ràng giữa `frontend-net` và `backend-net`, tuyệt đối không expose trực tiếp port Database ra bên ngoài.
- **Security Headers:** Cấu hình đầy đủ `X-Frame-Options`, `X-XSS-Protection`, `X-Content-Type-Options` trên Nginx.
- **Strong Credentials:** Sử dụng mật khẩu độ phức tạp cao cho toàn bộ dịch vụ và hệ thống.

---

## 🚀 Hướng Dẫn Khởi Chạy Hệ Thống

### 1. Kéo mã nguồn từ GitHub

Mở terminal và thực hiện clone dự án về máy:

```bash
# Clone repository từ GitHub
git clone https://github.com/dtc245200030/StudentManagement_v2.0.git

# Di chuyển vào thư mục dự án
cd student-management-system
```
### 2. Khởi tạo chứng chỉ SSL

Tạo thư mục lưu trữ và khởi tạo chứng chỉ Self-signed SSL cho Nginx:

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=localhost"
```

### 3. Khởi chạy tất cả Container

```bash
docker compose up -d --build
```

---

## 🌐 Danh Sách Dịch Vụ & Cổng Truy Cập

| Dịch vụ | Địa chỉ truy cập | Tài khoản mặc định |
| :--- | :--- | :--- |
| **Website (Flask + Nginx SSL)** | `https://localhost` | - |
| **Database Management (phpMyAdmin)** | `http://localhost:8081` | Theo cấu hình `.env` |
| **Monitoring & Logging (Grafana)** | `http://localhost:3000` | `admin` / `admin` |
| **Prometheus Metrics** | `http://localhost:9090` | - |

---

## 📝 Giấy Phép & Bản Quyền

Đồ án được thực hiện phục vụ cho mục đích học tập và nghiên cứu trong môn học **Triển khai & Quản trị Phần mềm**.
