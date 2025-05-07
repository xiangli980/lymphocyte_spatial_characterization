# Base image with CUDA support
FROM nvidia/cuda:12.9.0-cudnn-devel-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/conda/bin:${PATH}"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    openslide-tools \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -b -p /opt/conda \
    && rm /tmp/miniconda.sh

# Set up working directory
WORKDIR /app

# Copy environment files
COPY environments/ /app/environments/

# Create conda environments from yml files and install additional pip packages
# 1. HoverNet environment (cell_segmentation)
RUN conda env create -f /app/environments/hovernet_env.yml && \
    /opt/conda/envs/env_hover/bin/pip install -r /app/environments/hover_pip.txt

# 2. Graph Tool environment (cell_graph)
RUN conda env create -f /app/environments/graph_env.yml && \
    /opt/conda/envs/env_gt/bin/pip install -r /app/environments/graph_pip.txt

# 3. Patch Registration environment
RUN conda env create -f /app/environments/registration_env.yml && \
    /opt/conda/envs/env_reg/bin/pip install -r /app/environments/registration_pip.txt

# Copy project files
COPY spatial_characterization /app/spatial_characterization

# Create activation scripts for each environment
RUN echo '#!/bin/bash\n\
source /opt/conda/etc/profile.d/conda.sh\n\
conda activate env_hover\n\
exec "$@"' > /usr/local/bin/hover-env && \
    chmod +x /usr/local/bin/hover-env

RUN echo '#!/bin/bash\n\
source /opt/conda/etc/profile.d/conda.sh\n\
conda activate env_gt\n\
exec "$@"' > /usr/local/bin/gt-env && \
    chmod +x /usr/local/bin/gt-env

RUN echo '#!/bin/bash\n\
source /opt/conda/etc/profile.d/conda.sh\n\
conda activate env_reg\n\
exec "$@"' > /usr/local/bin/reg-env && \
    chmod +x /usr/local/bin/reg-env

# Create entrypoint script with usage instructions
RUN echo '#!/bin/bash\n\
echo "Spatial Characterization Toolkit"\n\
echo "Available environments:"\n\
echo "  hover-env: Activate HoverNet environment for cell segmentation"\n\
echo "  gt-env: Activate Graph Tool environment for cell graph analysis"\n\
echo "  reg-env: Activate Registration environment for patch registration"\n\
echo "Example usage:"\n\
echo "  hover-env python /app/spatial_characterization/cell_segmentation/run_tile.py"\n\
echo "  gt-env python /app/spatial_characterization/cell_graph/run_graph.py"\n\
echo "  reg-env jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root"\n\
exec "$@"' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
