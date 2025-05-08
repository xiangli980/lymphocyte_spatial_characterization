# Cell Graph Analysis

This module provides tools for analyzing cellular spatial organization by constructing and analyzing cell graphs from segmented cell data.

## Overview

The Cell Graph Analysis module takes segmented cell data (typically from the cell_segmentation module) and constructs graph representations of cellular spatial organization. It then extracts various graph-based features that can be used for downstream analysis of tissue architecture and cellular interactions.

## Features

- Construction of cell graphs from segmented cell data
- Region-of-interest (ROI) based analysis using masks
- Extraction of graph-based features including:
  - Clustering coefficient
  - Average shortest path length
  - Graph diameter
  - Average degree
  - K-core decomposition metrics
  - Assortativity correlation
  - Betweenness centrality metrics
  - Central point dominance
  - Eigenvector centrality
- Visualization of cell graphs overlaid on original images

## Files

### Python Scripts

- `run_graph.py`: Main script for processing cell images, creating graphs, and extracting features
- `run_graph_mask.py`: Similar to run_graph.py but uses masks to filter cells based on regions of interest
- `utils.py`: Utility functions for drawing graphs and extracting features

### Shell Scripts

- `run_graph.sh`: Example script for running run_graph.py with specific parameters
- `run_graph_mask.sh`: Example script for running run_graph_mask.py with specific parameters
- `run_graph_test.sh`: Script for testing the graph analysis on sample data

### Jupyter Notebooks

- `count.ipynb`: Notebook for counting and analyzing cell types in segmented data
- `get_mask.ipynb`: Notebook for creating and manipulating region-of-interest masks

### Sample Data

- `Annotation (Necrosis) Region 1.png`: Example annotation mask for necrotic regions
- `Annotation (Tumor) Region 1.png`: Example annotation mask for tumor regions

## Usage

### Basic Usage

To run the graph analysis on segmented cell data:

```bash
python run_graph.py \
  --input_dir_img="/path/to/images" \
  --input_dir_mat="/path/to/segmentation/mat" \
  --output_dir="/path/to/output" \
  --marker_size=0.1 \
  --line_width=0.3 \
  --cell_dist=40
```

### With Region-of-Interest Masks

To run the graph analysis with region-of-interest masks:

```bash
python run_graph_mask.py \
  --input_dir_img="/path/to/images" \
  --input_dir_mat="/path/to/segmentation/mat" \
  --input_dir_msk="/path/to/masks" \
  --output_dir="/path/to/output" \
  --marker_size=0.1 \
  --line_width=0.3 \
  --cell_dist=70
```

### Testing

To run a test on the sample data:

```bash
./run_graph_test.sh
```

This test script uses input files (images and cell mat files) from the cell_segmentation module's "test_data/output" folder as shown in the script:

```bash
python run_graph.py \
--input_dir_img="../cell_segmentation/test_data/input" \
--input_dir_mat="../cell_segmentation/test_data/output/mat" \
--output_dir="./test_graph_output" \
--marker_size=0.1 \
--line_width=0.3 \
--cell_dist=40 \
```

## Parameters

- `--input_dir_img`: Directory containing input images
- `--input_dir_mat`: Directory containing cell instance mat files (from segmentation)
- `--input_dir_msk`: Directory containing ROI mask files (for run_graph_mask.py)
- `--output_dir`: Directory for output files
- `--marker_size`: Marker size for drawing graph overlay (default: 2)
- `--line_width`: Line width for drawing graph overlay (default: 1)
- `--cell_dist`: Distance threshold to connect cells in graph (default: 40)

## Output

The scripts generate the following outputs:

1. Graph visualizations:
   - Overlay of graph on original image (`{name}_overlay.png`)
   - Graph visualization (`{name}_graph_{cell_dist}.png` or `.svg`)
   - Graph Tool format file (`{name}_graph.gt`)

2. Feature extraction:
   - CSV file with graph features for all processed images (`features_for_folder.csv`)

## Dependencies

- Python 3.x
- NumPy
- Pandas
- SciPy
- scikit-image
- Matplotlib
- graph-tool
- PIL (Pillow)
- OpenCV (cv2)
- tqdm

## Integration with Other Modules

This module is designed to work with the output from the cell_segmentation module, which provides the segmented cell data in MAT format. The output features can be used for further analysis and classification of tissue regions.
