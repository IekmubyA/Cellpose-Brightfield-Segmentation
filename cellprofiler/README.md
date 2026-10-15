# CellProfiler pipelines

This directory contains the CellProfiler pipelines used for fluorescence
background/illumination correction and quantitative per-cell feature extraction.

The workflow consists of two main CellProfiler stages:

1. fluorescence illumination/background correction
2. per-cell feature measurement and export to SQLite

Cellpose-derived segmentation masks are used to define cellular objects for
feature extraction.

---

## Directory structure

    cellprofiler/
    ├── README.md
    ├── illumination/
    │   ├── README.md
    │   └── REFERENCE_default_illumination.cppipe
    └── measurements/
        ├── README.md
        ├── training_pipeline_full_multichannel.cppipe
        └── training_pipeline_GFP_only.cppipe

---

## 1. Illumination correction

See:

`illumination/`

The reference CellProfiler pipeline is used independently for fluorescence
channels requiring correction.

In the study, the same correction procedure was applied separately to:

- GFP
- Hoechst
- Propidium iodide (PI)

Brightfield images were not corrected using this procedure.

The corrected fluorescence images were subsequently used for quantitative
feature extraction.

---

## 2. Feature extraction

See:

`measurements/`

Two measurement pipelines are provided.

### Full multichannel pipeline

`training_pipeline_full_multichannel.cppipe`

Designed for datasets containing:

- Brightfield
- GFP
- Hoechst
- Propidium iodide
- Cellpose-derived cell masks

This pipeline generates morphological and image-derived measurements used for
GFP and viability classification.

### GFP-only pipeline

`training_pipeline_GFP_only.cppipe`

Designed for datasets containing:

- Brightfield
- GFP
- Cellpose-derived cell masks

This reduced pipeline is intended for GFP-oriented datasets where Hoechst and
PI channels are not available.

---

## Output

The measurement pipelines export per-cell measurements to an SQLite database
for downstream analysis.

CellProfiler Analyst configuration files, training datasets, and trained
classification models are provided separately in:

`../cellprofiler_analyst/`

---

## Software

The pipelines were used with CellProfiler 4.2.8.
