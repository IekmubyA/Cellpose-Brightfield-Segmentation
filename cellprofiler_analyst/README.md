# CellProfiler Analyst classification models

This directory contains the CellProfiler Analyst (CPA) configuration files,
training datasets, and trained Gradient Boosting models used for cell-level
classification in the microscopy workflow.

Two independent classification tasks were used:

1. GFP-positive / GFP-negative classification
2. Cell viability and morphological-state classification

The corresponding per-cell measurements were generated using the CellProfiler
measurement pipelines provided in:

`../cellprofiler/measurements/`

---

## Directory structure

    cellprofiler_analyst/
    ├── README.md
    ├── configs/
    │   ├── Cells_GFP.properties
    │   └── Cells_VIABILITY.properties
    ├── training_sets/
    │   ├── TrainingSet_MASTER_v004.csv
    │   └── TrainingSet_MASTER_v001.csv
    └── models/
        ├── GFP_GradientBoosting_MASTER_v004_1128cells.model
        └── ITOG_____VIABILITY_GB_MASTER_v001_1275cells_CV84.31.model

---

## GFP classifier

The GFP classifier distinguishes GFP-negative and GFP-positive cellular objects.

The final training dataset contains 1,128 manually annotated cells:

- GFP-negative: 606
- GFP-positive: 522

The corresponding file is:

`training_sets/TrainingSet_MASTER_v004.csv`

The CSV contains 269 columns:

- `ImageNumber`
- `ObjectNumber`
- `Class`
- 266 numerical classifier features

The classifier was trained using the Gradient Boosting algorithm.

Five-fold cross-validation yielded an overall classification accuracy of
87.77%.

The final serialized model contains the same 266 input features.

Measurements derived from Hoechst/DAPI and propidium iodide (PI) were excluded
from the GFP classifier. The classifier therefore uses the remaining compatible
morphological and image-derived measurements, including features derived from
Brightfield and GFP images.

The exact feature-exclusion rules are defined in:

`configs/Cells_GFP.properties`

---

## Viability classifier

The viability classifier assigns cellular objects to five manually defined
classes:

- `alive`
- `apoptotic`
- `PIpositive`
- `deadnonuc`
- `empty`

The final training dataset contains 1,275 manually annotated objects:

- alive: 286
- apoptotic: 230
- PIpositive: 296
- deadnonuc: 226
- empty: 237

The corresponding file is:

`training_sets/TrainingSet_MASTER_v001.csv`

The CSV contains 296 columns:

- `ImageNumber`
- `ObjectNumber`
- `Class`
- 293 numerical classifier features

The classifier was trained using the Gradient Boosting algorithm.

The archived five-fold cross-validation report gives an overall classification
accuracy of 84.16%. The historical model filename contains `CV84.31`; the
original model filename is preserved unchanged in this repository.

The final serialized model contains the same 293 input features.

GFP-derived measurements were excluded from the viability classifier so that
cell-state classification was independent of GFP reporter expression.

The exact feature-exclusion rules are defined in:

`configs/Cells_VIABILITY.properties`

---

## Training datasets

The files in `training_sets/` contain the manually assigned class labels and
the numerical per-cell features used for classifier training.

Each row corresponds to one annotated cellular object and contains:

- the source `ImageNumber`
- the `ObjectNumber` within that image
- the manually assigned `Class`
- the numerical CellProfiler features used as classifier input

The original microscopy images are not included in this repository. Therefore,
the training CSV files allow inspection of the labels and numerical feature
space and can be used for computational re-training or benchmarking, but they
do not by themselves provide the original image crops for visual re-evaluation
of individual manual annotations.

---

## Feature exclusion rules

Both classifier configurations exclude technical or non-biological database
variables from model input, including:

- image identifiers
- object identifiers
- Parent/Children relationship measurements
- metadata fields
- spatial X/Y coordinates
- other technical database columns

Additional task-specific exclusions were applied.

### GFP model

Measurements derived from:

- Hoechst / DAPI
- Propidium iodide (PI)

were excluded.

### Viability model

Measurements derived from:

- GFP

were excluded.

The `.properties` files contain the exact regular-expression rules used for
these exclusions.

---

## CPA configuration files

The supplied `.properties` files define:

- SQLite database type and table names
- image and object identifiers
- microscopy image channels
- object-coordinate columns
- classifier feature-exclusion rules
- CellProfiler Analyst object-classification settings

For portability, the repository versions use the placeholder:

`PATH_TO_CELLS_DB/Cells.db`

in the `db_sqlite_file` field.

Before using the configuration files, replace this placeholder with the path
to a compatible local `Cells.db` file.

All classifier feature-exclusion rules are otherwise preserved from the
analysis configuration.

---

## Required measurements

The models expect per-cell measurements compatible with the CellProfiler
measurement pipelines distributed with this repository.

The full multichannel workflow uses:

- Brightfield
- GFP
- Hoechst
- Propidium iodide
- Cellpose-derived cell masks

The GFP classifier does not use Hoechst or PI measurements as model features,
although these channels may still be present in the source database.

The viability classifier does not use GFP-derived measurements as model
features.

---

## Model compatibility

The supplied model files are serialized scikit-learn Gradient Boosting
classifiers.

The serialized models were created using:

`scikit-learn 0.24.2`

Compatibility with substantially newer scikit-learn versions is not guaranteed.
For direct model loading, a compatible Python / scikit-learn environment or the
corresponding CellProfiler Analyst environment is recommended.

---

## Software

Cellular measurements were generated using CellProfiler 4.2.8.

Classification and manual cell annotation were performed using CellProfiler
Analyst.

Both classifiers use scikit-learn Gradient Boosting models trained on manually
annotated cellular objects.
