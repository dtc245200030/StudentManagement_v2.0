# Hệ Thống Quản Lý Sinh Viên - Đồ Án Triển Khai & Quản Trị Phần Mềm

Hệ thống Quản lý Sinh viên được đóng gói hoàn chỉnh bằng Docker Compose, tích hợp Nginx Reverse Proxy (SSL/TLS), giám sát Prometheus/Grafana, thu thập log tập trung Loki/Promtail và áp dụng các giải pháp Hardening bảo mật.

## 🛠 Công Nghệ Sử Dụng
- **Frontend/Backend:** Flask (Python)
- **Database:** MySQL 8.0 & phpMyAdmin
- **Reverse Proxy:** Nginx (HTTPS Self-signed & Security Headers)
- **Monitoring:** Prometheus, Grafana, cAdvisor
- **Logging:** Grafana Loki, Promtail
- **Containerization:** Docker, Docker Compose

## 🔒 Các Biện Pháp Hardening Đã Áp Dụng
1. **Non-root Container:** Chạy Flask App dưới dạng `appuser` hạn chế quyền.
2. **Network Isolation:** Phân chia `frontend-net` và `backend-net`, không expose trực tiếp port Database ra bên ngoài.
3. **Security Headers:** Cấu hình `X-Frame-Options`, `X-XSS-Protection`, `X-Content-Type-Options` trên Nginx.
4. **Strong Credentials:** Sử dụng mật khẩu độ phức tạp cao cho toàn bộ dịch vụ.

## 🚀 Hướng Dẫn Khởi Chạy Hệ Thống

### 1. Khởi tạo chứng chỉ SSL
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=localhost"
