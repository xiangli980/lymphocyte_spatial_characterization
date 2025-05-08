# Spatial Characterization

A toolkit for spatial characterization of tissue images, including cell segmentation, cell graph analysis, and patch registration.

## Components

### 1. Cell Segmentation (HoverNet)

The cell segmentation component uses HoverNet to segment and classify cells in tissue images. It provides:

- Nuclei segmentation
- Cell type classification
- Instance segmentation

### 2. Cell Graph Analysis

The cell graph analysis component constructs graphs from segmented cells and extracts features:

- Graph construction from cell centroids
- Feature extraction (clustering coefficient, shortest path, etc.)
- Visualization of cell graphs

### 3. Patch Registration

The patch registration component aligns and registers image patches:

- Registration of H&E and IHC images
- Nuclei detection using StarDist
- Mask generation

## Installation & Usage

### Using Docker (Recommended)

```bash
# Pull the latest image
docker pull username/spatial_characterization:latest

# Run the container with NAS storage mounted to /DataMount
docker run -it -v /path/to/nas/storage:/DataMount username/spatial_characterization:latest
```

### Data Storage

The container expects data to be mounted at `/DataMount`. This should be linked to your NAS storage location:

```bash
# Example with specific NAS path
docker run -it -v /mnt/nas/data:/DataMount username/spatial_characterization:latest
```

All scripts and workflows are configured to use paths within the `/DataMount` directory.

### Running Components

#### Cell Segmentation

```bash
# Run cell segmentation on a directory of images
docker run -it -v /path/to/nas/storage:/DataMount username/spatial_characterization:latest hover-env python /app/spatial_characterization/cell_segmentation/run_tile.py --input_dir=/DataMount/input --output_dir=/DataMount/output
```

#### Cell Graph Analysis

```bash
# Run cell graph analysis
docker run -it -v /path/to/nas/storage:/DataMount username/spatial_characterization:latest gt-env python /app/spatial_characterization/cell_graph/run_graph.py --input_dir_img=/DataMount/images --input_dir_mat=/DataMount/segmentation --output_dir=/DataMount/graphs
```

#### Patch Registration

```bash
# Run Jupyter notebook for patch registration
docker run -it -p 8888:8888 -v /path/to/nas/storage:/DataMount username/spatial_characterization:latest reg-env jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

## Development Workflow

### Best Practice for Making Changes

If you want to modify the code and still incorporate updates from the main repository, follow this workflow:

1. **Clone from GitHub**
   ```bash
   git clone https://github.com/username/spatial_characterization.git
   cd spatial_characterization
   ```

2. **Mount as Volume**
   ```bash
   # Run container with your local code mounted and NAS storage
   docker run -it -v $(pwd):/app/spatial_characterization -v /path/to/nas/storage:/DataMount username/spatial_characterization:latest
   ```

3. **Make Changes**
   - Edit files in your local directory
   - Changes are automatically available inside the container
   - Test your changes within the container environment

4. **Pull Updates**
   ```bash
   # Add the original repository as a remote (if not already done)
   git remote add upstream https://github.com/username/spatial_characterization.git
   
   # Fetch the latest changes
   git fetch upstream
   
   # Merge updates with your modifications
   git merge upstream/main
   ```

5. **Resolve Conflicts (if any)**
   - If there are conflicts between your changes and the updates
   - Resolve them using your preferred Git tools
   - Test that everything works after merging

6. **Build Custom Image (Optional)**
   ```bash
   # If you need to customize the environment
   docker build -t my-spatial-characterization .
   ```

### Alternative: Working Directly in Containers

If you prefer to work directly inside the container:

1. Make your changes inside the running container
2. When finished, save the container state:
   ```bash
   docker commit container_id my-spatial-characterization
   ```
3. To extract your changes for sharing or backup:
   ```bash
   # Create a temporary container and copy files out
   docker run --name temp-container -d my-spatial-characterization
   docker cp temp-container:/app/spatial_characterization /path/to/save/changes
   docker rm temp-container
   ```

## Updating Package Versions

To update package versions for any of the environments:

### For Conda Packages

1. Edit the appropriate environment YAML file in the `environments/` directory:
   - `hovernet_env.yml` for cell segmentation conda packages
   - `graph_env.yml` for cell graph analysis conda packages
   - `registration_env.yml` for patch registration conda packages

2. Update the version specifications as needed:
   ```yaml
   dependencies:
     - python=3.8
     - numpy=1.21.0  # Updated version
   ```

### For Pip Packages

1. Edit the appropriate pip requirements file in the `environments/` directory:
   - `hover_pip.txt` for cell segmentation pip packages
   - `graph_pip.txt` for cell graph analysis pip packages
   - `registration_pip.txt` for patch registration pip packages

2. Update the version specifications as needed:
   ```
   torch==1.8.0  # Updated version
   ```

### Rebuilding the Docker Image

After updating any package versions:

1. Rebuild the Docker image:
   ```bash
   docker build -t username/spatial_characterization:latest .
   ```

2. Push the updated image to Docker Hub:
   ```bash
   docker push username/spatial_characterization:latest
   ```

3. Tag the new version (optional):
   ```bash
   docker tag username/spatial_characterization:latest username/spatial_characterization:v1.1.0
   docker push username/spatial_characterization:v1.1.0
   ```

Users can then pull the updated image to get the new package versions.

## Original Usage Instructions

### Hover-Net Cell Segmentation & Classification
```bash
conda activate env_hover
cd cell_segmentation
# modify run_tile.sh
# --input_dir=/DataMount/path/to/input
# --output_dir=/DataMount/path/to/output
chmod +x run_tile.sh
./run_tile.sh
```

### Lymphocyte Graph Construction 
```bash
conda activate env_gt
cd cell_graph
python run_graph.py --input_dir_img /DataMount/path/to/images --input_dir_mat /DataMount/path/to/segmentation --output_dir /DataMount/path/to/output
```
