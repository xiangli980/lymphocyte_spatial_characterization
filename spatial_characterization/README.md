# spatial_characterization
 
# Hover-Net Cell Segmentation & Classification
conda activate env_hover
cd cell_segmenation
// modify run_tile.sh
// --input_dir=/DataMount/xl260/test/ROI
// --output_dir=/DataMount/xl260/test/Output_seg
chmod +x run_tile.sh
./run_tile sh

# Lymphocyte Graph Construction 
conda activate env_gt
cd cell_graph
python run_graph.py --input_dir path/to/input --output_dir path/to/output  
// example:
python run_graph.py --input_dir_img /DataMount/xl260/test/ROI --input_dir_mat /DataMount/xl260/test/Output_seg/mat --output_dir /DataMount/xl260/test/Output_graph 
