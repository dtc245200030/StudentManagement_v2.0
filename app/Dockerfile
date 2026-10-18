FROM python:3.10-slim

# Tạo user không phải root (Hardening - Non-root container)
RUN useradd -m appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Chuyển quyền sở hữu và chuyển đổi user
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000
CMD ["python", "app.py"]
