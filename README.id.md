# The Replica Skill (Bahasa Indonesia)

> Baca dalam bahasa lain: [English (README.md)](./README.md)

Sebelas skill Claude untuk mengkloning aplikasi apa pun. Gratis, berlisensi MIT, tanpa pendaftaran, tanpa API key, dan tidak ada layanan eksternal yang wajib dihubungkan.

Satu skill melakukan *reverse-engineering* terhadap aplikasi yang ingin Anda kloning. Satu skill membangunnya kembali. Satu skill mengujinya untuk mencari bug. Dan satu lagi adalah **Entrepreneur**: membaca apa yang dibenci pengguna aplikasi asli dari ulasan nyata, lalu memperbaikinya di versi Anda sehingga Anda memiliki produk yang layak dijual.

Di antaranya, skill lainnya merencanakan *tech stack* dan database, membangun ulang sistem desain (*design system*), menghubungkan autentikasi dan pembayaran, menilai skor kemiripan kloning Anda dibanding aplikasi asli, memberi nama dan identitas merek baru milik Anda sendiri, menulis *landing page* serta deskripsi *app store*, hingga menayangkannya secara langsung di domain Anda.

**Skill ini membangun ulang apa yang dilakukan sebuah aplikasi, bukan apa yang dimilikinya.** Fitur dan alur kerja dibangun dengan gaya *clean-room* (ruang bersih). Bukan menyalin kode sumber, logo, teks pemasaran, maupun konten eksklusifnya. Ketentuan lengkapnya ada di bagian bawah, dan setiap skill menegakkan aturan ini secara ketat.

## Instalasi

Tempelkan perintah ini ke dalam Claude:

```
https://github.com/Jakeschincariol/replica-skill

install skill
```

Atau pasang sebagai plugin di Claude Code:

```
/plugin marketplace add Jakeschincariol/replica-skill
/plugin install replica-skill@replica-skill
```

Claude Code memberikan *namespace* pada skill plugin, sehingga jika dipasang sebagai plugin perintahnya akan muncul sebagai `/replica-skill:replica-recon` dan seterusnya. Salin foldernya secara langsung jika Anda menginginkan perintah pendek seperti `/replica-recon`:

```bash
git clone https://github.com/Jakeschincariol/replica-skill.git
cp -r replica-skill/replica-* ~/.claude/skills/
```

Untuk penggunaan lokal per proyek (bukan global): salin folder yang sama ke dalam `.claude/skills/` di repositori proyek Anda. Tidak menggunakan Claude Code sama sekali? Tempelkan isi satu file `SKILL.md` di awal percakapan chat dan ia akan berjalan sebagai mode kerja. Anda memang tidak mendapatkan alat bantu Python secara otomatis di chat web, tetapi metodologinya tetap berjalan.

Alat bantu (*tools*) membutuhkan Python 3.8 atau yang lebih baru. Tidak perlu menjalankan `pip install` apa pun.

## Kesebelas Skill

| Perintah | Fungsi |
| --- | --- |
| `/replica-recon` | Melakukan *reverse-engineering* pada aplikasi apa pun: layar, alur kerja (*flows*), komponen, dan model data. Dari halaman publik, tangkapan layar (*screenshots*), daftar toko aplikasi, dan akun Anda sendiri. |
| `/replica-architect` | Merencanakan *tech stack*, skema database, dan API untuk kloning Anda. |
| `/replica-design` | Membangun ulang sistem desain: warna, tipografi, jarak (*spacing*), dan komponen dalam bentuk token desain dengan aset milik Anda sendiri. |
| `/replica-build` | Membangun ulang aplikasi layar demi layar berdasarkan peta hasil *recon*. |
| `/replica-backend` | Mengatur autentikasi, database, pembayaran, dan integrasi pihak ketiga. |
| `/replica-test` | Mengklik seluruh alur kerja dan mengujinya untuk menemukan bug (Playwright / Cypress). |
| `/replica-diff` | Membandingkan kloning Anda dengan aplikasi asli. Menghasilkan skor paritas dan daftar fitur yang masih kurang. |
| `/replica-entrepreneur` | Membaca keluhan pengguna aplikasi asli dari ulasan nyata dan mengubahnya menjadi rencana perbaikan serta sudut pandang pemasaran (*positioning angle*). |
| `/replica-brand` | Memberi nama dan mengubah identitas merek (*rebrand*) versi Anda agar sepenuhnya menjadi milik Anda. |
| `/replica-launch` | Menyiapkan *landing page*, strategi harga, serta materi pendaftaran App Store dan Google Play. |
| `/replica-deploy` | Menayangkan aplikasi secara langsung (*live*) di domain Anda sendiri. |

## Cara Penggunaan

Jalankan secara berurutan. Setiap skill membaca hasil yang ditulis oleh skill sebelumnya di dalam folder `replica/` pada proyek Anda.

```
recon -> architect -> design -> build -> backend -> test -> diff -> entrepreneur -> brand -> launch -> deploy
```

Contoh kasus: mengkloning aplikasi penjadwalan pertemuan (*scheduling app*), di mana Anda membagikan tautan dan orang lain dapat memilih jadwal bertemu dengan Anda.

1. **`/replica-recon`** dengan URL aplikasi target. Skill ini membaca pusat bantuan (*help center*), halaman harga, daftar toko aplikasi, dan panduan publik, lalu Anda mengklik akun Anda sendiri bersamanya. Hasilnya adalah `replica/recon.md`: 18 layar, 7 alur kerja (tamu memesan jadwal, tuan rumah mengatur ketersediaan waktu, tamu menjadwalkan ulang...), daftar komponen, model data yang disimpulkan (pengguna, jenis acara, ketersediaan, pemesanan), serta `features.csv`. *Marketplace* mitra ditandai di luar cakupan (*out of scope*): itu adalah jaringan mereka, bukan sebuah fitur.
2. **`/replica-architect`** memilih Next.js, Postgres, Stripe, dan Resend, menulis skema database (dengan batasan/*constraint* agar dua tamu tidak pernah bisa memesan slot waktu yang sama), lalu menyusun urutan pembangunan: alur pemesanan dari awal hingga akhir dibangun paling pertama.
3. **`/replica-design`** mengukur tangkapan layar menjadi token desain: peran warna, skala tipografi, jarak kelipatan 8px, serta spesifikasi pemilih tanggal (*date picker*) dan tombol slot waktu. Menggunakan ikon sumber terbuka, font terbuka, dan kalimat Anda sendiri.
4. **`/replica-build`** membangun kerangka utama (*shell*), dilanjutkan dengan alur pemesanan, lalu setiap layar beserta seluruh kondisinya (*states*), sambil mencentang `features.csv` seiring berjalannya proses.
5. **`/replica-backend`** menambahkan pendaftaran akun, integrasi Google Calendar melalui API resmi Google dengan kunci milik Anda sendiri, Stripe untuk pemesanan berbayar, serta email pengingat.
6. **`/replica-test`** menulis rencana pengujian dari ke-7 alur kerja, spesifikasi Playwright atau Cypress untuk jalur normal (*happy paths*) maupun kasus ekstrem (*edge cases* seperti zona waktu, slot yang diambil orang lain di tengah pemesanan, klik ganda pada tombol kirim), dan mencatat bug berdasarkan tingkat keparahan hingga tidak ada lagi bug S1 atau S2 yang terbuka.
7. **`/replica-diff`** menghitung skornya. Fitur 86, seluruh fitur wajib (*must-haves*) selesai, tata letak halaman pemesanan 91. Yang belum ada: pembagian jadwal bergilir (*round-robin*) untuk tim dan penyematan (*embed*) di situs web.
8. **`/replica-entrepreneur`** membaca 140 ulasan nyata dari App Store, G2, Capterra, dan Reddit. Keluhan teratas: lonjakan harga per kursi (*per-seat*), tidak adanya pengingat SMS, dan tamu yang bingung dengan zona waktu. Masing-masing dilengkapi jumlah kemunculan dan kutipan berpranala. Rencana perbaikan: harga tetap (*flat pricing*), pengingat SMS, dan langkah konfirmasi zona waktu. Sudut pandang pemasaran: tautan pemesanan jadwal untuk tim kecil yang membenci biaya per anggota.
9. **`/replica-brand`** memberi nama baru (lengkap dengan daftar pemeriksaan merek dagang dan domain yang harus dijalankan), palet warna baru, panduan logo, dan gaya bahasa, lalu menyapu seluruh basis kode hingga tidak ada satu pun jejak aplikasi asli yang tersisa.
10. **`/replica-launch`** menulis *landing page* berdasarkan sudut pandang pemasaran tersebut, menyusun harga yang bersaing dengan halaman publik aplikasi asli, dan memeriksa kepatuhan deskripsi toko aplikasi (*store listing*).
11. **`/replica-deploy`** menjalankan pemeriksaan pra-peluncuran (*preflight*: pengujian, paritas, sapuan merek, deskripsi toko), menyiapkan lingkungan produksi, memberikan catatan DNS untuk domain Anda, dan menayangkannya saat Anda memberi aba-aba.

Anda juga dapat menjalankan salah satu skill secara terpisah. Menjalankan `/replica-entrepreneur` pada aplikasi yang baru terpikirkan untuk Anda kloning adalah cara terbaik untuk mengetahui apakah ide tersebut layak dieksekusi.

## Alat Bantu (Tools)

Terdapat tujuh skrip alat bantu, semuanya hanya menggunakan pustaka standar (*standard library*) Python. Tidak ada satu pun yang mengakses jaringan internet.

```bash
python3 replica-diff/imgdiff.py original.png clone.png --out diff.png   # perbandingan tata letak, mengabaikan warna
python3 replica-diff/parity.py replica/features.csv                     # skor paritas + daftar fitur yang kurang
python3 replica-entrepreneur/reviews.py replica/reviews.csv             # apa yang dibenci pengguna, diurutkan & berpranala
python3 replica-design/contrast.py replica/design/tokens.json           # pemeriksaan kontras WCAG pada token desain
python3 replica-brand/sweep.py . --avoid "Original App"                 # apakah masih ada jejak aplikasi asli?
python3 replica-launch/listing.py replica/launch/listing.json           # batas karakter toko aplikasi + deteksi tiruan
python3 replica-deploy/preflight.py .                                   # menjalankan gerbang parity, contrast, sweep, listing
```

**`imgdiff.py`** membaca file PNG tanpa pustaka tambahan, mengubah kedua tangkapan layar menjadi peta tepi (*edge maps*), lalu membandingkan tata letak elemen sehingga warna baru Anda tidak dianggap sebagai kesalahan. Alat ini memberi tahu bagian mana yang berbeda dalam koordinat piksel gambar asli.

**`parity.py`** memberi bobot pada prioritas *must*, *should*, dan *could*, menghitung status *partial* sebagai setengah poin, dan tidak pernah memasukkan fitur yang sengaja Anda lewati atau fitur tambahan baru ke dalam perhitungan skor paritas. Jika masih ada fitur *must-have* yang belum selesai, aplikasi dinyatakan belum layak rilis.

**`reviews.py`** membuang setiap ulasan yang tidak memiliki tautan sumber. Setiap kutipan yang ditampilkan disalin persis dari baris data yang Anda berikan beserta URL-nya. Tema keluhan dengan kurang dari tiga ulasan atau hanya berasal dari satu sumber akan ditandai sebagai data tipis (*thin*).

**`contrast.py`** memeriksa rasio kontras WCAG 2.2 untuk kode warna Hex (`#fff`), `rgb()`/`rgba()`, maupun `hsl()`/`hsla()` pada token desain Anda.

**`sweep.py`** mencari nama aplikasi asli, domain, dan kode warnanya di seluruh kode proyek Anda, termasuk di dalam nama pengenal seperti `OriginalAppEmbed`, serta memblokir proses rilis hingga semuanya bersih (mendukung file UTF-8 maupun UTF-16).

**`listing.py`** memeriksa batas panjang karakter App Store dan Google Play, klaim peringkat berlebihan pada judul, pemborosan karakter kata kunci, serta penyebutan nama aplikasi asli di dalam metadata toko Anda.

**`preflight.py`** menjalankan pemeriksaan `parity`, `contrast`, `sweep`, dan `listing` sekaligus dalam satu perintah sebelum aplikasi ditayangkan ke publik.

Untuk menjalankan pengujian unit (*unit tests*):

```bash
# Di Linux / macOS:
python3 -m unittest discover -s tests -v

# Di Windows:
run_tests.bat
```

## Ketentuan Penting (Fine Print)

**Membangun ulang fungsionalitas dan pola UX dengan gaya *clean-room*.** Skill ini mempelajari apa yang dilakukan aplikasi dan bagaimana pengguna berinteraksi di dalamnya, lalu menulis semuanya dari nol. Skill ini tidak pernah menyalin kode sumber target, aset berhak cipta, logo, merek dagang, teks pemasaran, maupun API privat.

**Hanya membaca apa yang diizinkan untuk Anda baca.** Halaman publik dan akun milik Anda sendiri. Tidak pernah melakukan *scraping* di balik halaman login atau melanggar ketentuan layanan situs, tidak pernah masuk ke akun orang lain, dan tidak pernah menerobos dinding berbayar (*paywall*). Jika ketentuan akun Anda melarang penggunaannya untuk membangun produk pesaing, skill ini akan memberi tahu Anda dan hanya menggunakan sumber publik.

**Selalu melakukan *rebranding* sebelum peluncuran.** Nama baru, palet warna baru, logo baru, dan kalimat baru. `/replica-deploy` tidak akan menayangkan aplikasi sampai pemeriksaan `sweep.py` dinyatakan bersih.

**"Mengkloning aplikasi apa pun" berarti fitur dan alur kerjanya.** Bukan konten, jaringan pengguna, atau lisensi yang dimiliki aplikasi tersebut. Anda dapat membangun ulang pemutar musik, daftar putar, dan fitur berbagi dari sebuah aplikasi musik, tetapi Anda tidak dapat mengkloning katalog lagunya.

**Tidak ada jaminan kloning yang "sempurna".** Hasil akhir bergantung pada seberapa kompleks aplikasi targetnya. Alat pemesanan jadwal dapat selesai dalam hitungan minggu, sedangkan mesin *spreadsheet* tidak. `/replica-recon` memperkirakan ukuran pekerjaan secara jujur sebelum Anda mulai, dan `/replica-diff` memberikan angka terukur, bukan sekadar perkiraan kasar.

**Skill Entrepreneur tidak pernah mengarang data.** Tidak ada ulasan, kutipan, atau angka fiktif. Setiap klaim memiliki tautan sumber dan ukuran sampelnya disebutkan secara jelas.

**Periksa kembali sebelum Anda menjual.** Jalankan pemeriksaan merek dagang yang dicantumkan oleh `/replica-brand`, baca ketentuan layanan dari setiap hal yang Anda gunakan, dan konsultasikan dengan ahli hukum sebelum peluncuran komersial. Dokumentasi ini bukan merupakan nasihat hukum.

## Daftar File

```
replica-recon/         SKILL.md, recon-map.md, features.csv (templat matriks fitur)
replica-architect/     SKILL.md, architecture.md
replica-design/        SKILL.md, tokens.json, contrast.py
replica-build/         SKILL.md
replica-backend/       SKILL.md
replica-test/          SKILL.md, test-plan.md, bug-report.md, e2e.example.spec.ts, cypress.example.cy.ts
replica-diff/          SKILL.md, imgdiff.py, parity.py
replica-entrepreneur/  SKILL.md, reviews.py, themes.json
replica-brand/         SKILL.md, sweep.py
replica-launch/        SKILL.md, listing.py, listing.example.json
replica-deploy/        SKILL.md, preflight.md, preflight.py
tests/                 pengujian unit untuk seluruh alat bantu
```

File kerja proyek Anda sendiri disimpan di dalam folder `replica/` pada proyek Anda. Kesebelas skill saling membaca file di dalam folder tersebut.

## Kredit

Dibuat oleh Jake Schincariol, [opusjake.ai](https://opusjake.ai). Proyek serupa:
[Arena](https://github.com/Jakeschincariol/arena-skill),
[X](https://github.com/Jakeschincariol/x-agent-skill),
[LinkedIn](https://github.com/Jakeschincariol/linkedin-agent-skill),
[Instagram](https://github.com/Jakeschincariol/instagram-agent-skill).

## Lisensi

MIT. Gunakan, ubah, dan luncurkan.
