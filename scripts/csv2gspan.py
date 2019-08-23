#!/usr/bin/env python3

# This script is used to convert csv files extracted from graph database
# to a format used by gSpan

import csv, sys, os, time

# path for data files
path      = os.path.dirname(os.path.abspath(__file__)) + "/../data"

fieldname1 = ['id', 'label']
fieldname2 = ['id', 'word']
fieldname3 = ['start_id', 'end_id', 'label', 'type']

# csv files must be present in the following paths
csv_files = [path + '/graphs_csv/main_nodes.csv',
             path + '/graphs_csv/nodes_',
             path + '/graphs_csv/relationships_']

NE_CNT    = 8 # Number of different named entities
NEWS_CNT  = 0 # Number of news to be converted (will be set later)

main_nodes = []
ne_check   = [0] * NE_CNT
neids      = list(range(0, NE_CNT))

if (__name__== "__main__"):
    try:
        # script takes 2 arguments
        # 1st : which news to start from (0 based indexed)
        # 2nd : how many news should be converted
        start_nid = int(sys.argv[1])
        specified_count = int(sys.argv[2])
    except:
        # default arguments
        start_nid = 0
        specified_count = None
    with open(csv_files[0], 'r') as f:
        main_nodes_file = csv.DictReader(f, fieldnames=fieldname1)
        for row in main_nodes_file:
            if (row['id'] == 'id'):
                continue
            main_nodes.append(row)

    # if count is not specified, all news will be converted starting from the first one
    # if that is the case, do not consider named entities (as they are also in main nodes) 
    NEWS_CNT = (start_nid + specified_count) if specified_count else int(len(main_nodes[:-NE_CNT]))
    
    # output file
    gspan_file = open(path + '/graph.gspan.data', 'w+')

    # conversion
    for i in range(start_nid, NEWS_CNT):
        edges          = []
        vertices       = []
        ne_check       = [0] * NE_CNT
        vertex_counter = 1
        nodes_label2id = {}
        nid = int(main_nodes[i]['id'])
        
        # Graph Definition
        t = "t # " + str(i) + "\n"
        gspan_file.write(t)
        v = "v 0 " + str(NE_CNT + 2) + "\n"
        vertices.append(v)
        if nid not in nodes_label2id:
            nodes_label2id[nid] = 0
        
        # Vertex Definition
        with open(csv_files[1] + str(i) + ".csv", 'r') as f_node:
            nodes_file = csv.DictReader(f_node, fieldnames=fieldname2)
            for row in nodes_file:
                if (row['id'] == 'id'):
                    continue
                wid = int(row['id'])
                v = "v " + str(vertex_counter) + " " + str(wid + 2) + "\n"
                vertices.append(v)
                if wid not in nodes_label2id:
                    nodes_label2id[wid] = vertex_counter
                vertex_counter += 1
        
        with open(csv_files[2] + str(i) + ".csv", 'r') as f_rel:
            rels_file = csv.DictReader(f_rel, fieldnames=fieldname3)
            for row in rels_file:
                if (row['start_id'] == 'start_id') or not row['start_id']:
                    continue
                rid  = int(row['label'])
                rsid = int(row['start_id'])
                if rsid in neids and not ne_check[rsid]:
                    v = "v " + str(vertex_counter) + " " + str(rsid + 2) + "\n"
                    vertices.append(v)
                    nodes_label2id[rsid] = vertex_counter
                    vertex_counter += 1
                    ne_check[rsid] = 1
                sid = nodes_label2id[rsid]

                reid = int(row['end_id'])
                if reid in neids and not ne_check[reid]:
                    v = "v " + str(vertex_counter) + " " + str(reid + 2) + "\n"
                    vertices.append(v)
                    nodes_label2id[reid] = vertex_counter
                    vertex_counter += 1
                    ne_check[reid] = 1
                eid = nodes_label2id[reid]

                e = "e " + str(sid) + " " + str(eid) + " " + str(rid) + "\n"
                edges.append(e)
        gspan_file.writelines(vertices)
        gspan_file.writelines(edges)
    gspan_file.write("t # -1\n")
    gspan_file.close()
