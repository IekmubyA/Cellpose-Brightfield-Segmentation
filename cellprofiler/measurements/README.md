# CellProfiler feature extraction and database export

This directory contains the CellProfiler pipelines used for quantitative
feature extraction from segmented microscopy images and export of per-cell
measurements to SQLite databases.

## Pipelines

### `training_pipeline_full_multichannel.cppipe`

Pipeline for datasets containing:

- Brightfield images
- GFP images
- Hoechst images
- Propidium iodide (PI) images
- Cellpose cell masks (`MasksCell`)

The pipeline measures per-cell morphological and image-derived features,
including:

- object size and shape
- fluorescence intensity
- granularity
- texture
- intensity distribution
- Hoechst/PI colocalization

Objects touching image or mask borders are excluded before measurement.
Measurements are exported to an SQLite database using CellProfiler's
`ExportToDatabase` module.

### `training_pipeline_GFP_only.cppipe`

Reduced pipeline for datasets containing:

- Brightfield images
- GFP images
- Cellpose cell masks (`MasksCell`)

This pipeline is intended for GFP-oriented datasets for which Hoechst and
propidium iodide channels are not available.

## Input files

The pipelines were used with images and Cellpose-derived masks supplied to
CellProfiler as matched image sets. File locations and input lists may need
to be adapted to the user's local directory structure before execution.

## Software

The pipelines were used with CellProfiler 4.2.8.
