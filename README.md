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
```

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
```

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
```

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
