import argparse
import pandas as pd
import numpy as np
import os
import scipy.io as sio
import skimage.io as skio
import graph_tool.all as gt
from tqdm import tqdm
from utils import draw_graph_overlay, get_feature
from PIL import Image
Image.MAX_IMAGE_PIXELS = None


def read_files(img_path, mat_path):
    """Read image and mat files"""
    img = skio.imread(img_path, plugin='pil')
    inst_info = sio.loadmat(mat_path)
    inst_centroids = inst_info['inst_centroid']
    inst_types = inst_info['inst_type']
    return img, inst_centroids, inst_types

def draw_graph(g, img, points, name, output_dir, marker_size, line_width, cell_dist=40):
    """Draw graph on image"""
    edges = g.get_edges()
    draw_graph_overlay(edges, img, points, name, output_dir, marker_size, line_width)
    # draw the graph independently using graph-tool inherent function
    # gt.graph_draw(g, pos=g.vp['pos'], output = './Dataset/{}_graph.png'.format(name))
    gt.graph_draw(g, pos=g.vp['pos'], vprops = {"fill_color" : 'yellow', "size" : marker_size}, 
                  eprops = {"pen_width" : line_width, "color":'cyan'}, bg_color='black', 
                  output = os.path.join(output_dir, 'graph', '{}_graph_{}.png'.format(name, cell_dist)))
    
def process_graph(inst_centroids, inst_types, name, cell_dist=40):
    """create graph and extract features"""
    # Get lymphocyte points == 2, tumor == 1
    points = []
    for centroid, inst_type in zip(inst_centroids, inst_types):
        if inst_type[0] == 1:
            x0, y0 = centroid[0], centroid[1]
            points.append([x0,y0])
    points = np.array(points)
    
    # create a graph
    connect = cell_dist # connect distance setting
    g, pos = gt.geometric_graph(points, connect)
    g.set_directed(False)
    g.vertex_properties["pos"] = pos
    # extract features   
    f = get_feature(g, name)
    return g, f, points

def check_count(inst_types, name):
    """ Check for lymphocytes """
    uni, cnt = np.unique(inst_types, return_counts=True)
    # class: 0 - background, 1 - other cells, 2 - lymphocytes
    # if uni not contain 2 then no lymphocytes in the image
    if 2 not in uni: # skip this image
        print(f'{name} has no lymphocytes')
        return False 
    else:
        # print number of lymphocytes and other cells
        # count of lymphocytes is in cnt[2] and other cells in other cnt values
        print(f'{name} has {cnt[-1]} lymphocytes and {sum(cnt[:])-cnt[-1]} other cells') 
        return True 



def main():
    parser = argparse.ArgumentParser(description='Process cell images and create graphs')
    parser.add_argument('--input_dir_img', type=str, required=True, 
                        help='Directory containing input images')
    parser.add_argument('--input_dir_mat', type=str, required=True, 
                        help='Directory containing cell instance mat files')
    parser.add_argument('--output_dir', type=str, required=True,
                        help='Directory for output files')
    parser.add_argument('--marker_size', type=float, default=2,
                        help='Marker size for drawing graph overlay')
    parser.add_argument('--line_width', type=float, default=1, 
                        help='Line width for drawing graph overlay')
    parser.add_argument('--cell_dist', type=float, default=40, 
                        help='Distance to connect cells in graph')
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, 'feature'), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, 'graph'), exist_ok=True)

    # Initialize DataFrame
    df = pd.DataFrame(columns=['ROI','clus','clus_dev', 'avg_dist', 'diameter', 
                             'avg_degree', 'num_nodes', 'max_kcore', 'mean_kcore', 
                             'freq_kcore','num_kcore', 'corr_mean','corr_var', 'avg_betweenness', 
                             'num_high_betweenness', 'central_node_dom', 
                             'eigenvector_centrality'])

    # Get list of files
    names = [f.split('.')[0] for f in os.listdir(args.input_dir_mat) if f.endswith('.mat')]

    # Process each image
    for name in tqdm(names):
        img_path = os.path.join(args.input_dir_img, f'{name}.png')
        mat_path = os.path.join(args.input_dir_mat, f'{name}.mat')
        cell_dist = args.cell_dist

        # Read files
        img, inst_centroids, inst_types = read_files(img_path, mat_path)
        
        # # Check for lymphocytes
        # if not check_count(inst_types, name):
        #     continue    

        # create graph, extract features and add to dataframe
        g, f, points = process_graph(inst_centroids, inst_types, name, cell_dist)
        
        # check if f exist?
        # add features to dataframe
        df = pd.concat([df, pd.DataFrame(f,index=[0])], ignore_index=True)

        # visualize the graph
        draw_graph(g, img, points, name, args.output_dir, args.marker_size, args.line_width, cell_dist)
    
        # save the graph
        g.save(os.path.join(args.output_dir, 'graph', '{}_graph.gt'.format(name)))  
        
    # Save feature extraction results for all images
    df.to_csv(os.path.join(args.output_dir, 'feature', 'features_for_folder.csv'), index=False)

if __name__ == '__main__':
    main()