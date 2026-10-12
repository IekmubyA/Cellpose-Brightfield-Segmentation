# Cellpose Brightfield Segmentation

A small graphical interface for sequential segmentation of 2D brightfield TIFF images using a user-supplied trained Cellpose model.

The script processes all `.tif` and `.tiff` files located directly in the selected input folder and creates:

- `MasksCell/` — TIFF segmentation masks
- `Segmentation/` — JPEG previews with cell boundaries

Subfolders are not scanned, and the original TIFF images are not modified.

## Requirements

A working Python environment with Cellpose must be installed separately. The selected environment should contain Cellpose, PyTorch, and the scientific Python dependencies required by Cellpose and this script.

For GPU processing, the selected PyTorch installation must have working CUDA support. CPU processing can be used by clearing the **Use GPU (CUDA)** option.

The Windows launcher only opens the graphical interface. It does not install Cellpose, PyTorch, CUDA, or the trained model.

## Running on Windows

1. Download or clone this repository.
2. Double-click `Launch_Cellpose_Simple.bat`.
3. In the GUI, select the `python.exe` from your Cellpose environment.
4. Select the folder containing the input TIFF images.
5. Select the trained Cellpose model file.
6. Select an empty output folder.
7. Enable or disable **Use GPU (CUDA)** as appropriate.
8. Click **Start segmentation**.

The GUI can also be started directly with:

```bash
python Cellpose_Simple_GUI.py
```

## Segmentation parameters

The following parameters are fixed in the script:

- `flow_threshold = 0.6`
- `cellprob_threshold = 0.0`
- normalization percentiles: `1–99`
- JPEG preview quality: `95`

Images are processed sequentially, one TIFF at a time.

## Input

The input folder should contain 2D brightfield TIFF images.

Supported extensions:

- `.tif`
- `.tiff`

## Output

For an input image such as:

```text
image_001.tif
```

the program creates:

```text
OutputFolder/
├── MasksCell/
│   └── image_001.tif
└── Segmentation/
    └── image_001.jpg
```

The trained Cellpose model is not included in this repository and must be supplied separately.
