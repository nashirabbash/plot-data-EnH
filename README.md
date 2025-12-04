# Audiogram Plotter - Enhanced Version

Aplikasi unified untuk plotting audiogram dari 2 jenis data berbeda: **Elbicare** dan **Pychoacoustics**.

## 🎯 Fitur Utama

### 1. Plot Elbicare

- **Format file**: HT\_\*.TXT (JSON format dengan field `ampl`)
- **Frekuensi**: 250 Hz - 8000 Hz (standar audiogram, skip 125 Hz)
- **Kalibrasi**: Otomatis load `calib_example.json`
- **Output**: Plot dalam **dBA** (sesuai kalibrasi)

### 2. Plot Pychoacoustics

- **Format file**: TXT plain text dengan `turnpointMean`
- **Frekuensi**: 125 Hz - 8000 Hz (standar audiogram lengkap)
- **Konversi**: dB SPL → dB HL menggunakan **RETSPL (IEC 60318)**
- **Output**: Plot dalam **dB HL** (inverted Y-axis)

## 📊 Standar Plot

- **X-axis**: Logarithmic scale, **125 - 8000 Hz** (untuk semua jenis data)
  - Frequencies: 125, 250, 500, 1000, 2000, 4000, 8000 Hz
- **Y-axis**: **-20 (atas) hingga 160 (bawah) dB** - Inverted (untuk semua jenis data)
  - Standar audiogram convention
  - Semakin ke bawah = semakin parah hearing loss

## 🚀 Cara Penggunaan

1. **Jalankan aplikasi**:

   ```bash
   python audiogram_plotter.py
   ```

2. **Pilih jenis data**:

   - Klik **"Plot Elbicare"** untuk file HT\_\*.TXT
   - Klik **"Plot Pyco Acoustic"** untuk file pychoacoustics TXT

3. **Upload file TXT** sesuai format

4. **Lihat hasil plot** dan data PTA di console

## 📁 File Structure

```
plotEnh/
├── audiogram_plotter.py    # Main application
├── calib_example.json       # Calibration file untuk Elbicare
├── requirements.txt         # Dependencies list
└── README.md                # Dokumentasi ini
```

## 🔧 Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd plotEnh
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Application

```bash
python audiogram_plotter.py
```

### Requirements

- Python 3.7 atau lebih baru
- PyQt5 >= 5.15.0
- matplotlib >= 3.5.0
- numpy >= 1.21.0

## 📝 Format Data

### Elbicare (HT\_\*.TXT)

```json
{
  "audiogram": {
    "ch_0": {
      "freq_0": {"freq": 0.625, "ampl": 2},
      "freq_1": {"freq": 1.250, "ampl": 5},
      ...
    },
    "ch_1": { ... }
  }
}
```

**Penting**:

- `freq` di file adalah label (0.625-20 kHz)
- Sebenarnya mapping ke standar: 250-8000 Hz
- `ampl` dikonversi via `calib_example.json`

### Pychoacoustics (Plain TXT)

```
Ear: Right
Frequency (Hz): 250
turnpointMean = 39.17, s.d. = 3.01
```

**Konversi**:

- `turnpointMean` = dB SPL
- dB HL = dB SPL - RETSPL

## 📐 RETSPL Values (IEC 60318)

| Frequency (Hz) | RETSPL (dB) |
| -------------- | ----------- |
| 125            | 45.0        |
| 250            | 27.0        |
| 500            | 13.5        |
| 1000           | 7.5         |
| 2000           | 9.0         |
| 4000           | 12.0        |
| 8000           | 15.5        |

## 📊 PTA Calculation

**Pure Tone Average** menggunakan 4 frekuensi:

- 500 Hz
- 1000 Hz
- 2000 Hz
- 4000 Hz

Formula: `PTA = (dB500 + dB1000 + dB2000 + dB4000) / 4`

## ⚠️ Catatan Penting

1. **Elbicare TIDAK menggunakan RETSPL** - hanya kalibrasi via JSON
2. **Pychoacoustics menggunakan RETSPL** untuk konversi dB SPL → dB HL
3. **Plot sudah distandarkan**:
   - X-axis: 125-8000 Hz (logarithmic)
   - Y-axis: -20 hingga 160 dB (inverted - standar audiogram)
   - Kedua jenis data menggunakan format plot yang sama
4. **Elbicare data freq 125 Hz**: Tidak ada data (plot mulai dari 250 Hz)

## 📞 Support

Untuk pertanyaan atau bug report, silakan hubungi developer.

---

**Version**: 2.0  
**Last Updated**: December 2025
