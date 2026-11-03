# 1. Base Image Python
FROM python:3.11-slim

# 2. Set working directory di dalam kontainer
WORKDIR /app

# 3. Salin file requirements dan install dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Salin kode aplikasi dan artefak model terbaik
COPY app.py .
COPY model.pkl .

# 5. Expose port 5000 (sesuai port Flask)
EXPOSE 5000

# 6. Jalankan aplikasi
CMD ["python", "app.py"]