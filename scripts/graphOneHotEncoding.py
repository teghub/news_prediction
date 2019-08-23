#! /usr/bin/env python3

import os, sys, re, time, csv, pickle
import numpy as np
import multiprocessing as mp
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity as cs
from scipy.stats.stats import pearsonr
from sklearn.preprocessing import OneHotEncoder

CURR_DIR = os.getcwd()
sys.path.insert(0, os.path.join(CURR_DIR, 'gSpan'))
from graph4teghub import Graph
import gspan_mining

K              = 20
GRAPHS_DIR     = os.path.join(CURR_DIR, '..', 'data', 'reduced25.pkl')
INPUT_PATH     = os.path.join(CURR_DIR, '..', 'data')
GRAPHS         = {}
ENCODINGS      = {}
FILES          = ['words.csv', 'news.csv', 'named_entities.csv']
FIELDNAMES     = [['wid:ID', ':LABEL', 'word'],
                  ['nid:ID', ':LABEL', 'label'],
                  ['neid:ID', ':LABEL', 'name']]
SIM_ALGOS      = ['Cosine', 'Euclidean Distance', 'Pearson']
SIMILAR_GRAPHS = {}
VOCAB          = {}

def get_top_k_cosine_sim(graph_id, k):
    all_sim = np.array([(key, cs(ENCODINGS[graph_id], ENCODINGS[key])[0][0]) 
                        for key in tqdm(ENCODINGS, 
                                        desc="Calculating Cosine Simlarity for Graph " + 
                                             str(graph_id))],
                        dtype=[('key', int), ('sim', float)])
    all_sim = np.sort(all_sim, order='sim')[::-1]
    return all_sim[1:k + 1]

def get_cosine_sim(i, j):
    return cs(ENCODINGS[i], ENCODINGS[j])[0][0]

def generate_vocab(graphs):
    VOCAB = {}
    for graph in tqdm(graphs.values(), desc="Generating Vocab"):
        for nlbl in graph.set_of_nlbl:
            if nlbl not in VOCAB:
                VOCAB[nlbl]  = 1
            else:
                VOCAB[nlbl] += 1
    return VOCAB

def _get_encoding(data):
    graph_id, graph = data
    return (graph_id, np.array(graph.get_OneHotEncoding(list(VOCAB.keys())).reshape(1, -1)))

def get_encodings():
    with mp.Pool(os.cpu_count()) as p:
        all_encodings = p.map(_get_encoding, GRAPHS.items())
    for graph_id, embedding in all_encodings:
        ENCODINGS[graph_id] = embedding


def _create_graph(graph_id, graphObj):
    graph = Graph(gid=graph_id, export_path=INPUT_PATH)
    graph.create_from_gSpanObj(graphObj)
    GRAPHS[graph_id] = graph

def import_from_list(graph_list):
    GRAPH_CNT = 0
    for graph in graph_list.values():
        _create_graph(GRAPH_CNT, graph)
        GRAPH_CNT += 1

def import_graphs_from_file():
    with (open(GRAPHS_DIR, "rb")) as f:
        subgraphs = pickle.loads(f.read())
        import_from_list(subgraphs)

def print_similarities(results):
    for _id, sim in results:
        print(_id, '->', sim)
    print("-" * 20)

def _init_gohe(subgraphs):
    global VOCAB, GRAPHS
    import_from_list(subgraphs) 
    VOCAB = generate_vocab(GRAPHS)
    get_encodings()

def get_clusters(subgraphs, threshold, init_gohe=True):
    if init_gohe:
        _init_gohe(subgraphs)

    assigned_clusters = {}
    cluster_id = 0

    for graph_id in tqdm(GRAPHS, desc='Clustering'):
        if graph_id in assigned_clusters:
            continue
        all_sim = np.array([(key, cs(ENCODINGS[graph_id], ENCODINGS[key])[0][0])
                                for key in ENCODINGS],
                                dtype=[('key', int), ('sim', float)])
        all_sim = np.sort(all_sim, order='key')
        for i in range(len(all_sim)):
            if all_sim[i][1] > threshold:
                if i not in assigned_clusters:
                    assigned_clusters[i] = cluster_id
        cluster_id += 1

    clusters = {}
    for k, v in assigned_clusters.items():
        if v in clusters:
            clusters[v].append(k)
        else:
            clusters[v] = [k]

    return clusters

if (__name__ == "__main__"):
    import_graphs_from_file()
    
    print("-" * 60)
    print("Generating Vocabulary...")
    VOCAB = generate_vocab(GRAPHS)
    print("# of Items in VOCAB:", len(VOCAB))
    print("-" * 60)
    
    print("Getting One Hot Encodings of the Graphs...")
    get_encodings()
    print("Done!")
    print("-" * 60)

    print("Moving to similarity calculation...")
    for i in range(len(GRAPHS)):
        try:
            results = get_top_k_cosine_sim(i, K)
            print("-" * 60)
            print_similarities(results)
            answer = input()
            if str(answer).lower() == 'q':
                break
        except KeyboardInterrupt:
            break
