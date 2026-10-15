# CellProfiler fluorescence background correction

This directory contains the reference CellProfiler pipeline used for background correction of fluorescence microscopy images.

## Files

- [`REFERENCE_default_illumination.cppipe`](REFERENCE_default_illumination.cppipe) — a single-channel CellProfiler pipeline applied **separately** to GFP, Hoechst, and propidium iodide (PI) images.

The same pipeline settings were used for all three fluorescence channels. Brightfield images were **not** background-corrected by this procedure.

## Processing settings

The pipeline uses `CorrectIlluminationCalculate` followed by `CorrectIlluminationApply` and `SaveImages`:

| Parameter | Setting |
| --- | --- |
| Illumination estimation | `Background` |
| Scope | `Each` (independently for each image) |
| Block size | `200` |
| Smoothing | `Fit Polynomial` |
| Smoothing filter size | `30` |
| Application | `Subtract` |
| Clip values below 0 / above 1 | `Yes` / `Yes` |
| Output | 8-bit TIFF |

Segmentation masks were **not** used to exclude cell regions during background estimation.

## Input and execution notes

The provided `.cppipe` was saved from a processing workflow that supplies an explicit list of TIFF images to CellProfiler for **one channel at a time**. The output directory is supplied at runtime. It does not contain an embedded list of image paths.

To use it independently, configure CellProfiler to load the TIFF files for **one fluorescence channel** and choose an appropriate output directory. Repeat for GFP, Hoechst, and PI separately. Check the image-set selection and output paths in your CellProfiler setup before starting a batch run.

This repository provides the scientific pipeline configuration, not the original local workflow manager used to automate file selection. No proprietary microscopy images or experimental databases are included.
