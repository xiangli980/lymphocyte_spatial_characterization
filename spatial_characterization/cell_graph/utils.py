import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import graph_tool.all as gt
import os

def draw_graph_overlay(edges, img, points, name, output_dir, marker_size=2, line_width=1):
    # figure size
    plt.figure(figsize=(6, 6))
    # plot edges 
    for e in edges:
        plt.plot([points[e[0]][0],points[e[1]][0]],[points[e[0]][1],points[e[1]][1]],color = 'cyan', linewidth=line_width)
    # plot points
    plt.plot(points[:,0], points[:,1], color = 'cyan', marker ='o', markersize=marker_size, linestyle = 'None')
    # plot image
    plt.imshow(img)
    plt.axis('off')
    plt.title('{}'.format(name))
    plt.savefig(os.path.join(output_dir, 'graph', '{}_overlay.png'.format(name)), 
                dpi=300, bbox_inches='tight')
    plt.close()



def get_feature(g, name): 
    # chack if the graph has edge
    # calculate the weight of the edges
    weight = g.new_edge_property("double")
    for e in g.edges():
        weight[e] = np.linalg.norm(g.vp["pos"][e.target()].a - g.vp["pos"][e.source()].a)
    g.edge_properties["weight"] = weight

    # feature - clustering coefficieo
    clus, dev_clus= gt.global_clustering(g) # weight
    # feature - average shortest path length
    dist_list = []
    for v in g.vertices():
        dist = gt.shortest_distance(g, source=v,  weights=g.ep.weight)
        dist_list.append(np.max(dist.a[~np.isinf(dist.a)]))
    avg_dist = np.mean(dist_list)
    # feature - diameter
    diameter = np.max(dist_list)
    # feature - average degree
    avg_degree = np.mean(g.get_total_degrees(g.get_vertices()))
    # feature - number of nodes
    num_nodes = g.num_vertices()
    # feature - kcore 
    kcore = gt.kcore_decomposition(g)
    max_kcore = np.max(kcore.fa)
    mean_kcore = np.mean(kcore.fa)
    freq_kcore = len(np.unique(kcore.fa)) # number of different kcore values
    #print(np.unique(kcore.fa))
    num_kcore = np.sum(kcore.fa == max_kcore) # number of groups that have max kcore number
    # feature - correlation
    corr_mean, corr_var = gt.assortativity(g, 'total')  # eweight
    # featue - betweenness centrality
    vb, eb = gt.betweenness(g) # weight
    # feature - average betweenness centrality
    avg_betweenness = np.mean(vb.fa)
    # feature - number of nodes with high betweenness centrality
    num_high_betweenness = np.sum(vb.fa > np.mean(vb.fa))/g.num_vertices()
    # feature - central node
    cd = gt.central_point_dominance(g, vb)
    # eigrn vector centrality
    ee, x = gt.eigenvector(g, max_iter=1000)
    # featrues to add to dataframe
    new_f = {"ROI": name,'clus':clus, 'clus_dev':dev_clus, 'avg_dist':avg_dist, 'diameter':diameter, 'avg_degree':avg_degree, 'num_nodes':np.array(num_nodes).max(), 'max_kcore':np.array(max_kcore).max(), 'mean_kcore':np.array(mean_kcore).max(), 'freq_kcore':freq_kcore, 'num_kcore':np.array(num_kcore).max(), 'corr_mean':corr_mean,'corr_var':corr_var, 'avg_betweenness':np.array(avg_betweenness).max(), 'num_high_betweenness':np.array(num_high_betweenness).max(), 'central_node_dom':cd, 'eigenvector_centrality':ee}
    return new_f
