# Dataset Inspection & Technical Feasibility Report

**Project:** Multimodal AI Health Assistant  
**Date:** September 18, 2026  
**Status:** Initial Dataset Audit Completed  

---

## 1. Executive Summary

This report presents a thorough technical inspection of all five medical datasets provided for the **Multimodal AI Health Assistant**. The datasets encompass four distinct clinical modalities:
1. **Clinical Tabular Data (Cerebrovascular)**: Stroke prediction records (`stroke_prediction.csv`).
2. **Clinical Tabular Data (Cardiovascular)**: Heart disease diagnostic metrics (`heart.csv`).
3. **1D Biosignals**: Electrocardiogram (ECG) waveforms (`.mat` files).
4. **2D Radiological Imaging**: Chest X-ray images (`.jpeg`).
5. **3D/Volumetric Medical Imaging**: Computed Tomography (CT) scans (`.dcm` DICOM format).

### Critical Finding on Patient Record Cross-Linking
> **Can patient records be directly linked across datasets?**  
> **NO.** The 5 datasets originate from completely distinct research and clinical cohorts across different institutions worldwide. None of the datasets share patient identifiers, medical record numbers, or AP numbers:
> - `stroke_prediction.csv` uses arbitrary de-identified integer IDs (`67` to `72940`).
> - `heart.csv` contains zero patient identifiers.
> - ECG `.mat` files are MIT-BIH Arrhythmia Database segment files named after PhysioNet tape records (e.g., `213m (3).mat`).
> - Chest X-rays originate from pediatric pneumonia studies with names like `person78_virus_140.jpeg`.
> - CT images originate from The Cancer Genome Atlas (TCGA) lung/chest series (`TCGA-17-Z034`).
>
> **Prototype Solution:** In accordance with the system design, we implement a **Local SQLite Patient Registry & Record Mapping Schema**. This maps realistic composite patient profiles (`AP-1001`, `AP-1002`, etc.) with authentic records and raw files from each modality, enabling end-to-end multimodal dashboard operation and AI assistant retrieval.

---

## 2. Dataset Specifics

### Dataset 1: Stroke Prediction Dataset (`stroke_prediction.csv`)
* **File Format:** CSV (Comma-Separated Values)
* **Number of Records:** 5,110 rows × 12 columns
* **Patient Identifiers:** `id` column (unique 5,110 integers, ranging from 67 to 72,940). No link to other datasets.
* **Columns & Data Types:**
  - `id` (*int64*): Unique subject identifier
  - `gender` (*object*): 'Male' (2,115), 'Female' (2,994), 'Other' (1)
  - `age` (*float64*): Patient age (0.08 to 82.0 years, mean: 43.2)
  - `hypertension` (*int64*): 0 (No: 4,612), 1 (Yes: 498)
  - `heart_disease` (*int64*): 0 (No: 4,834), 1 (Yes: 276)
  - `ever_married` (*object*): 'Yes' (3,353), 'No' (1,757)
  - `work_type` (*object*): 'Private' (2,925), 'Self-employed' (819), 'Govt_job' (657), 'children' (687), 'Never_worked' (22)
  - `Residence_type` (*object*): 'Urban' (2,596), 'Rural' (2,514)
  - `avg_glucose_level` (*float64*): Blood glucose level (55.12 to 271.74 mg/dL, mean: 106.15)
  - `bmi` (*float64*): Body Mass Index (10.3 to 97.6, mean: 28.89)
  - `smoking_status` (*object*): 'never smoked' (1,892), 'Unknown' (1,544), 'formerly smoked' (885), 'smokes' (789)
  - `stroke` (*int64*): Target label
* **Target Label & Class Distribution:**
  - `0` (No Stroke): **4,861** (95.13%)
  - `1` (Stroke): **249** (4.87%)
  - *Significant class imbalance; requires class weighting or oversampling in subsequent training phase.*
* **Missing Values:**
  - `bmi`: 201 missing values (3.93%). Other columns have 0 missing values.

---

### Dataset 2: Heart Disease Tabular Dataset (`heart.csv`)
* **File Format:** CSV
* **Number of Records:** 1,025 rows × 14 columns
* **Patient Identifiers:** **None**. No patient ID, name, or MRN exists.
* **Columns & Clinical Significance:**
  - `age` (*int64*): Age in years (29 to 77, mean: 54.4)
  - `sex` (*int64*): 1 = Male (713), 0 = Female (312)
  - `cp` (*int64*): Chest pain type (0: Typical Angina, 1: Atypical Angina, 2: Non-anginal, 3: Asymptomatic)
  - `trestbps` (*int64*): Resting blood pressure (mm Hg on admission to hospital, 94 to 200)
  - `chol` (*int64*): Serum cholesterol in mg/dl (126 to 564)
  - `fbs` (*int64*): Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)
  - `restecg` (*int64*): Resting electrocardiographic results (0, 1, 2)
  - `thalach` (*int64*): Maximum heart rate achieved (71 to 202 bpm)
  - `exang` (*int64*): Exercise induced angina (1 = yes, 0 = no)
  - `oldpeak` (*float64*): ST depression induced by exercise relative to rest (0.0 to 6.2)
  - `slope` (*int64*): Slope of peak exercise ST segment (0, 1, 2)
  - `ca` (*int64*): Number of major vessels (0-4) colored by fluoroscopy
  - `thal` (*int64*): Thalassemia indicator (0, 1, 2, 3)
  - `target` (*int64*): Diagnosis of heart disease
* **Target Label & Class Distribution:**
  - `1` (Heart Disease Present): **526** (51.32%)
  - `0` (Heart Disease Absent): **499** (48.68%)
  - *Well-balanced binary distribution.*
* **Missing Values:** None (0 missing across all features).

---

### Dataset 3: ECG Signals Dataset (`.mat` files)
* **File Format:** MATLAB v5 / v7 `.mat` binary files
* **Total Signal Files:** 1,001 `.mat` records
* **Patient Identifiers:** None. Filenames (e.g. `213m (3).mat`, `100m (0).mat`) represent MIT-BIH Arrhythmia Database subject tape numbers, not clinical dashboard patient IDs.
* **ECG Signal Structure:**
  - Internal variable key: `'val'`
  - Array Shape: `(1, 3600)` (1D continuous digital lead recording)
  - Sampling Rate: 360 Hz (3,600 samples corresponds to exactly **10.0 seconds** of single-channel rhythm strip)
  - Lead: **MLII** (Modified Limb Lead II, standard rhythm strip configuration)
  - Amplitude Data Type: `int16` raw ADC units (calibrated centered around baseline ~1024)
* **Categories & Arrhythmia Class Distribution (17 Classes):**
  | Arrhythmia Class | Full Description | Number of Records |
  | :--- | :--- | :--- |
  | **1 NSR** | Normal Sinus Rhythm | 284 |
  | **4 AFIB** | Atrial Fibrillation | 135 |
  | **7 PVC** | Premature Ventricular Contraction | 133 |
  | **14 LBBBB** | Left Bundle Branch Block Beat | 103 |
  | **2 APB** | Atrial Premature Beat | 66 |
  | **15 RBBBB** | Right Bundle Branch Block Beat | 62 |
  | **8 Bigeminy** | Ventricular Bigeminy | 55 |
  | **17 PR** | Paced Rhythm | 45 |
  | **6 WPW** | Wolff-Parkinson-White Syndrome | 21 |
  | **3 AFL** | Atrial Flutter | 20 |
  | **9 Trigeminy** | Ventricular Trigeminy | 13 |
  | **5 SVTA** | Supraventricular Tachyarrhythmia | 13 |
  | **13 Fusion** | Fusion of Ventricular & Normal Beat | 11 |
  | **16 SDHB** | Sinoatrial / Heart Block Beat | 10 |
  | **10 VT** | Ventricular Tachycardia | 10 |
  | **12 VFL** | Ventricular Flutter | 10 |
  | **11 IVR** | Idioventricular Rhythm | 10 |

---

### Dataset 4: Chest X-Ray Dataset (`chest xray/`)
* **File Format:** Standard JPEG images (`.jpeg`)
* **Total Images:** 1,068 images
* **Directory Structure & Class Distribution:**
  - `chest xray/train/NORMAL`: **678** images (Normal paediatric chest radiographs)
  - `chest xray/test/PNEUMONIA`: **390** images (Consolidation/infiltrates present: bacterial and viral pneumonia)
* **Patient Identifiers:** Generic filenames like `person78_virus_140.jpeg`, `person83_bacteria_412.jpeg` contain subject codes, but have no metadata linkage to cardiovascular/stroke cohorts.
* **Image Structure:**
  - Resolution: High-resolution variable dimensions (approx. 1000×800 to 2000×1800 pixels)
  - Channels: 1 (Grayscale) / 3 (RGB encoded grayscale)
  - Bit Depth: 8-bit per channel

---

### Dataset 5: CT Medical Images Dataset (`CT_MedicalImages.zip`)
* **File Format:** DICOM (`.dcm` medical standard format)
* **Total Files:** 100 DICOM volumetric axial slices
* **Patient Identifiers:** TCGA Subject IDs (e.g. `TCGA-17-Z034`) embedded within DICOM standard metadata headers.
* **DICOM Header & Structural Attributes:**
  - `Modality`: CT (Computed Tomography)
  - `Matrix Dimensions`: 512 × 512 pixels
  - `Pixel Spacing`: `[0.78125 mm, 0.78125 mm]`
  - `Bit Depth / Data Type`: 16-bit unsigned integer (`uint16`)
  - `Contrast Bolus`: Tagged with CONTRAST status (0 = non-contrast, 1 = contrast enhanced)
  - `Patient Age`: Embedded (e.g., `060Y`)
  - `Patient Sex`: Embedded (`M` / `F`)

---

## 3. Cross-Dataset Harmonization Architecture

Since no universal patient identifier exists, the system uses a **Patient Registry and Multimodal Linkage Engine** in SQLite:

```
                  ┌───────────────────────────────┐
                  │    SQLite PATIENT REGISTRY    │
                  │  (AP Number, Name, Age, Sex)  │
                  └──────────────┬────────────────┘
                                 │
     ┌──────────────┬────────────┼────────────┬──────────────┐
     │              │            │            │              │
     ▼              ▼            ▼            ▼              ▼
Tabular Heart  Tabular Stroke  ECG Lead MLII  Chest X-ray    CT Scan
(1025 records) (5110 records)  (1001 strips)  (1068 images)  (100 slices)
```

Each patient profile in the registry has foreign-key mappings to:
1. Cardiovascular risk parameters (`trestbps`, `chol`, `thalach`, `restecg`)
2. Stroke risk factors (`hypertension`, `avg_glucose_level`, `bmi`, `smoking_status`)
3. Raw 10-second ECG waveform record (`.mat` filepath + sampling metadata)
4. Chest X-ray radiograph image (`.jpeg` filepath + radiological condition)
5. CT axial image (`.dcm` / `.png` filepath + Hounsfield windowing)

This design maintains 100% scientific authenticity: all signals, images, and clinical numbers visualized on the dashboard are genuine medical records from the respective validated datasets.
