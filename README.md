# stock-prediction

Proyek MLOps TIF B - FILKOM UB 2026. Digunakan untuk memprediksi pergerakan harga saham BUMI menggunakan data yang diambil melalui library yfinance.

Proyek ini merupakan implementasi dasar MLOps untuk membangun dan
mengelola pipeline machine learning yang digunakan untuk memprediksi
pergerakan harga saham BUMI berdasarkan data sentimen.

Pada tahap awal, proyek berfokus pada penyiapan struktur proyek,
lingkungan pengembangan menggunakan GitHub Codespaces, serta
penerapan version control dan branching strategy menggunakan GitHub Flow.

## Struktur Direktori

```text
MLOps-BUMI-Sentiment/
├── config/                 # File konfigurasi proyek
├── data/                   # Dataset yang digunakan
│   ├── raw/                # Data mentah
│   └── processed/          # Data yang telah diproses
├── models/                 # Penyimpanan model machine learning
├── notebooks/              # Jupyter Notebook untuk eksperimen
├── src/                    # Source code proyek
├── .devcontainer/          # Konfigurasi GitHub Codespaces
├── .gitignore              # File yang diabaikan oleh Git
├── LICENSE                 # Lisensi MIT
└── README.md               # Dokumentasi proyek
```

## Development Environment

Proyek ini menggunakan GitHub Codespaces sebagai lingkungan
pengembangan. Environment dikonfigurasi menggunakan Python 3.14.2
beserta beberapa ekstensi pendukung untuk pengembangan Python dan
Jupyter Notebook.

## Cara Menjalankan Proyek

1. Buka repository GitHub.
2. Klik tombol Code.
3. Pilih tab Codespaces.
4. Klik Create codespace on main.
5. Tunggu hingga proses setup environment selesai.
6. Buka terminal pada Codespaces.
7. Pastikan versi Python dengan menjalankan:

bash
python --version

8. Install dependency proyek dengan menjalankan:


bash
pip install -r requirements.txt

## Branching Strategy

Proyek ini menggunakan GitHub Flow dengan branch utama `main` dan branch pengembangan terpisah.
Branch yang digunakan untuk setup awal adalah:

`feat/initial-setup`

Setiap perubahan dikembangkan pada branch terpisah dan diajukan melalui Pull Request sebelum di-merge ke branch `main`.

## Lisensi

Proyek ini menggunakan lisensi MIT.

## Panduan Ekstraksi dan Prapemrosesan Data

Bagian ini menguraikan langkah-langkah teknis untuk menjalankan skrip pengumpulan (*ingestion*) dan pembersihan (*preprocessing*) data saham. 

### Prasyarat Sistem
Sebelum menjalankan skrip, pastikan Anda telah menginstal seluruh pustaka Python yang dibutuhkan. Jalankan perintah berikut pada terminal:

bash
pip install yfinance pandas

1. Pengumpulan Data Mentah (Data Ingestion)
Skrip ingest_data.py bertugas untuk mengunduh data historis saham selama satu tahun terakhir dari Yahoo Finance dan menyimpannya ke dalam direktori lokal.

Cara Menjalankan Skrip:
Jalankan perintah berikut dari root directory proyek Anda:

bash
python src/ingest_data.py

Output:
Skrip akan secara otomatis membuat folder data/raw/ (jika belum ada) dan menyimpan data mentah ke dalam format CSV dengan penamaan dinamis berdasarkan tanggal eksekusi (contoh: data/raw/bumi_YYYYMMDD.csv).

2. Prapemrosesan Data (Data Preprocessing)
Skrip preprocess.py berfungsi untuk memproses data mentah yang telah diunduh, secara spesifik membersihkan baris data yang memiliki nilai kosong (missing values) agar siap digunakan untuk analisis lanjutan.

Cara Menjalankan Skrip:
Setelah skrip ingestion berhasil dijalankan, eksekusi perintah berikut pada terminal:

Bash
python src/preprocess.py

Output:
Skrip akan membaca data mentah terbaru, menghapus nilai yang kosong, dan menyimpan data bersih ke dalam direktori data/processed/ dengan format penamaan (contoh: data/processed/bumi_bersih_YYYYMMDD.csv).

Alur Versioning & Manajemen Data dengan DVC

Berikut adalah dokumentasi langkah-langkah Data Version Control yang telah diterapkan pada proyek ini:

1. Inisialisasi DVC

Inisialisasi sistem tracking DVC di dalam repositori Git lokal:

dvc init
git add .dvc .gitignore
git commit -m "Initialize DVC"


2. Pelacakan Dataset Awal

Menambahkan dataset mentah ke pelacakan DVC. Langkah ini menghasilkan file pointer data/raw/bumi.csv.dvc serta memperbarui .gitignore agar file CSV besar tidak masuk ke Git:

python src/ingest_data.py
dvc add data/raw/bumi.csv
git add data/raw/bumi.csv.dvc data/raw/.gitignore
git commit -m "Track dataset awal bumi.csv dengan DVC"


3. Konfigurasi Local Remote Storage

Mengatur storage lokal terpisah sebagai simulasi remote storage DVC untuk sinkronisasi data:

# Menyiapkan direktori storage remote
mkdir -p /tmp/dvc-storage

# Menambahkan remote default ke DVC
dvc remote add -d myremote /tmp/dvc-storage
git add .dvc/config
git commit -m "Setup local remote storage untuk DVC"

# Mengunggah data ke remote storage
dvc push


4. Simulasi Continual Learning & Data Versioning

Saat data baru ditarik kembali (continual learning), DVC akan memperbarui hash (MD5) pada file pointer .dvc:

# Ingest data versi baru
python src/ingest_data.py

# Melacak perubahan versi data dengan DVC
dvc add data/raw/bumi.csv


5. Audit & Monitoring Perubahan Data (Diff)

Untuk melihat perbedaan hash/metadata antara versi data lama dan baru:

# Memeriksa status perubahan data
dvc status

# Memeriksa perbedaan versi hash MD5
dvc diff


6. Sinkronisasi & Reproduksi Versi Data

Untuk mengunggah versi data terbaru ke remote storage:

dvc push
git add data/raw/bumi.csv.dvc
git commit -m "Update dataset bumi.csv versi baru"
git push origin eksperimen


Untuk mengambil/mengembalikan versi data sesuai commit Git tertentu:

git checkout <commit-hash>
dvc checkout

## 🤖 Model Inferensi Aktif

* **Model Name:** Stock_Prediction_Model
* **Active Version:** Version 1 (Production Stage)
* **Alasan Pemilihan:** Model ini dipilih berdasarkan evaluasi di LK-06 karena memiliki nilai RMSE terendah dan $R^2$ tertinggi di antara eksperimen lainnya. Model ini di-export dari MLflow dan dibungkus ke dalam Docker Container untuk layanan inferensi.

## ⚙️ LK-08: Otomatisasi Pipeline "Code as a Trigger" (GitHub Actions)

Workflow: [`.github/workflows/mlops-automation.yaml`](.github/workflows/mlops-automation.yaml).
Dipicu otomatis oleh **push ke `main`** dan **pull request ke `main`** (bisa juga manual lewat tombol *Run workflow*).

| Tahap | Job | Isi |
|---|---|---|
| 1 | Automated Testing | `pytest -v` (folder `tests/`): preprocessing, fitur, metrik, gerbang evaluasi, config, dan API Flask |
| 2 | Automated Training | Tarik data terbaru (`src/ingest_data.py`) → versioning `dvc add data/raw/bumi.csv` → `src/train.py` dengan MLflow server di runner |
| 3 | Evaluation & Validation | `src/evaluate.py` membandingkan metrik dengan `config/thresholds.yaml`; gagal = pipeline berhenti |
| 4 | Auto-Registry Update | `src/register_model.py` mendaftarkan model ke MLflow Model Registry dengan stage **Staging** (+ alias `staging`) |

- Hyperparameter ada di `config/params.yaml`. Ubah nilainya lalu push/PR untuk memicu retraining.
- Threshold ada di `config/thresholds.yaml`. Akurasi arah UP/DOWN dibandingkan dengan target LK-01 (> 55%).
- Hasil MLflow (database registry + artefak model) bisa diunduh dari bagian **Artifacts** di halaman run GitHub Actions (`mlflow-registry`).

Menjalankan test di lokal:

```bash
pip install -r requirements-ci.txt
pytest -v
```


## 🐳 Menjalankan Seluruh Sistem dengan Docker Compose

Seluruh sistem (tracking server, inisialisasi model, dan API inferensi) berjalan dengan **satu perintah**:

```bash
docker compose up -d --build
```

| Layanan | Fungsi | Akses dari host |
|---|---|---|
| `mlflow-server` | MLflow tracking server + Model Registry. Database dan artefak disimpan di volume `mlflow-data`. | http://localhost:5000 |
| `model-trainer` | Tugas sekali jalan. Jika registry belum punya model `Stock_Prediction_Model@staging`, layanan ini menjalankan ingest → train → evaluate → register. Jika sudah ada, layanan ini langsung selesai. | - |
| `api-service` | API inferensi Flask. Saat start, API menarik model `models:/Stock_Prediction_Model@staging` dari `http://mlflow-server:5000`. | http://localhost:8000 |

- Semua layanan terhubung ke custom bridge network `mlops-net`, sehingga kontainer saling memanggil memakai nama layanan (mis. `http://mlflow-server:5000`).
- Urutan start diatur dengan `depends_on`: `mlflow-server` harus *healthy* → `model-trainer` harus selesai sukses → `api-service` mulai.
- Volume `mlflow-data` membuat registry dan artefak model tetap ada setelah `docker compose down`.

Perintah yang sering dipakai:

```bash
docker compose ps            # status layanan yang berjalan
docker compose ps -a         # termasuk model-trainer yang sudah selesai (Exited 0)
docker compose logs -f api-service

curl http://localhost:8000/health                       # menampilkan sumber & versi model dari MLflow
curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"Feature_Close_Lag1": 150.0}'

docker compose down          # hentikan sistem (data di volume tetap ada)
docker compose down -v       # hentikan sistem dan hapus volume (registry ikut terhapus)
```


## 🚀 Model Serving dengan MLflow Models & Horizontal Scaling

Model terbaik dilayani sebagai REST API dengan fungsi bawaan MLflow Models. Layanan ini berjalan dalam beberapa replika di belakang load balancer Nginx.

### 1. Naikkan model ke stage Production

```bash
MLFLOW_TRACKING_URI=http://localhost:5000 python src/promote_model.py
```

### 2. Serving lokal (tanpa Docker)

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
mlflow models serve -m "models:/Stock_Prediction_Model/Production" -p 5001 --env-manager local
```

### 3. Bangun image Docker untuk model

```bash
mlflow models build-docker -m "models:/Stock_Prediction_Model/Production" \
  -n stock-prediction/model-serving:v1 --env-manager local
```

### 4. Jalankan seluruh sistem (3 replika model)

```bash
docker compose up -d
docker compose ps        # model-serving-1, -2, -3 harus berstatus healthy
```

### Mengakses endpoint API

| Endpoint | Fungsi |
|---|---|
| `GET  http://localhost:8090/ping` | Memeriksa apakah layanan model siap |
| `POST http://localhost:8090/invocations` | Prediksi harga Close dari `Feature_Close_Lag1` |

Contoh request:

```bash
curl -X POST http://localhost:8090/invocations \
     -H "Content-Type: application/json" \
     -d '{"dataframe_split": {"columns": ["Feature_Close_Lag1"], "data": [[150.0], [200.0]]}}'
# {"predictions": [148.85..., 196.80...]}
```

Header respons `X-Served-By` menunjukkan IP replika yang melayani request.

### Menambah atau mengurangi jumlah replika secara dinamis

```bash
docker compose up -d --scale model-serving=5   # menjadi 5 replika
docker compose up -d --scale model-serving=3   # kembali ke 3 replika
```

Nginx membaca ulang DNS Docker setiap 10 detik. Replika baru langsung menerima request tanpa restart load balancer.
Setiap replika memakai 1 worker dan batas memori 512 MB (lihat `deploy.resources` di `docker-compose.yaml`).
