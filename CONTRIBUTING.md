# Panduan Kontribusi (Contributing Guide)

Terima kasih atas ketertarikan Anda untuk berkontribusi pada `replica-skill`! 

Berikut adalah panduan dan alur kerja agar Pull Request (PR) Anda mudah ditinjau dan diterima oleh maintainer repository upstream ([`Jakeschincariol/replica-skill`](https://github.com/Jakeschincariol/replica-skill)).

---

## 1. Aturan Emas Proyek (Golden Rules)

Sebelum membuat perubahan, perhatikan aturan ketat repositori ini:
1. **Zero External Dependencies**: Semua skrip pembantu (tools) harus hanya menggunakan modul bawaan Python (Standard Library murni). Jangan menambahkan dependensi `pip`.
2. **Kompabilitas Python 3.8+**: Skrip harus dapat berjalan di Python versi 3.8 sampai versi terbaru.
3. **No Em-Dashes**: Repositori memiliki tes otomatis yang melarang tanda baca em-dash (\u2014). Gunakan tanda hubung biasa (-), titik dua (:), atau format kalimat lain.
4. **Clean-Room Ethic**: Jangan memasukkan kode hak cipta, materi proprietary, aset grafis orisinal, atau scraper ilegal ke dalam repo.
5. **Setiap Fitur Baru Wajib Memiliki Test**: Tambahkan unit test baru di folder `tests/` jika mengubah atau menambah logika kode.

---

## 2. Alur Kerja Kontribusi (Step-by-Step)

```
[Fork Repo] -> [Sync Upstream] -> [Create Branch] -> [Coding & Testing] -> [Push & Open PR]
```

### Langkah 1: Hubungkan Remote Upstream
Pastikan repository lokal Anda terhubung dengan remote repositori asli:
```bash
git remote add upstream https://github.com/Jakeschincariol/replica-skill.git
git fetch upstream
```

### Langkah 2: Buat Branch Baru untuk Fitur/Perbaikan
Jangan membuat perubahan langsung di branch `main`:
```bash
git checkout main
git pull upstream main
git checkout -b feat/nama-perbaikan-anda
# Contoh:
# git checkout -b fix/windows-encoding-and-ci
```

### Langkah 3: Terapkan Perubahan & Jalankan Tes Lokal
Pastikan semua tes lolos sebelum melakukan commit:
* **Di Windows**:
  ```cmd
  run_tests.bat
  ```
* **Di Linux / macOS**:
  ```bash
  python3 -m unittest discover -s tests -p "test_*.py" -v
  ```

### Langkah 4: Commit Perubahan dengan Pesan yang Jelas
Gunakan konvensi commit yang rapi:
```bash
git add .
git commit -m "fix(sweep): handle UTF-16 encoded files and add CI workflow"
```

### Langkah 5: Push ke Fork Anda & Buat Pull Request
```bash
git push -u origin feat/nama-perbaikan-anda
```
Buka repository fork Anda di GitHub, lalu klik tombol **Compare & pull request**.

---

## 3. Template Deskripsi Pull Request

Gunakan struktur berikut saat mengisi deskripsi PR:

```markdown
### Summary of Changes
- Added CI workflow (.github/workflows/test.yml) to run test suite across Ubuntu, macOS, and Windows.
- Added UTF-16 decoding support in `replica-brand/sweep.py` to prevent missed scans on Windows PowerShell redirects.
- Added friendly error messages for JPEG/WebP files in `replica-diff/imgdiff.py`.
- Added unit tests covering all new edge cases.

### Motivation
Improves developer experience, cross-platform compatibility on Windows, and ensures continuous testing across Python 3.8-3.12 without introducing external dependencies.

### Verification
- [x] Ran unit tests locally (`python -m unittest discover -s tests`).
- [x] Zero external dependencies maintained.
- [x] Verified no em-dashes introduced.
```

