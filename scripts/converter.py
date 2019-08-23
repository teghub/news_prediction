#!/usr/bin/env python3

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# Importing FSM script
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
gSpan_path = os.path.join(currentdir, "gSpan")
sys.path.append(gSpan_path)
from gspan_mining.config import parser as gSpanParser
from gspan_mining.main import main

# Importing Other Scripts
import ruleMining as rm
import graphEditDistance as ged
import graphOneHotEncoding as gohe
import utils as utils
import pickle
import time

# News count
NE_CNT    = 8
neids     = list(range(0, NE_CNT))

# Relationship Types
rel_table = {1: "CONTAINS",
             2: "IS",
             3: "FOLLOWED_BY"}

# Printing Graph in textual format
def print_graph(g):
    print('Graph', g.gid)
    for v in g.vertices.values():
        print('\tVertice {} - Label {}'.format(v.vid, v.vlb))
        for e in v.edges.values():
            print ('\t\tEdge {} (Label {}) From {} To {}'.format(e.eid, e.elb, e.frm, e.to))
    # Uncomment next line for graphical representation of the graph
    #g.plot()

# Cheking if all the nodes are included or not
def _check_all_marked(check_list):
    if not check_list:
        return 0
    else:
        if 0 in check_list:
            return 0
        return 1

# Converting gSpan Graph to the Neo4j Query Format
def gSpan2query(g):
    """
    Given a gSpan graph, construct and return its query for database
    """
    print('Graph', g.gid)
    query      = "MATCH "
    return_q   = "RETURN "
    num_ver    = int(g.get_num_vertices())
    edge_id    = 0
    cnt_ver    = 0
    cnt_edge   = 0
    edge_flag  = 0
    check_list = [0] * num_ver
    for v in g.vertices.values():
        cnt_ver += 1
        vid = int(v.vid)
        vlb = int(v.vlb)
        num_of_edges = len(v.edges)
        return_q += "v" + str(vlb - 2)
        if cnt_ver != num_ver:
            return_q += ", "

        if not num_of_edges:            
            if check_list[vid] != 1:
                if (cnt_ver != 1):
                    query += "      "
                if (vlb - 2 in neids):
                    query += "(v" + str(vlb - 2) + ":NamedEntity " 
                    query += "{neid:" + str(vlb - 2) + "})"
                elif (vlb - 2 == NE_CNT):
                    query += "(v" + str(vlb - 2) + ":News)" 
                else:
                    query += "(v" + str(vlb - 2) + ":Word " 
                    query += "{wid:" + str(vlb - 2) + "})"
                check_list[vid] = 1
                if (cnt_ver == num_ver):
                    query += "\n"
                else:
                    if not (_check_all_marked(check_list)):
                        query += ", \n" 
                    else:
                        query += "\n"
        
        cnt_edge = 0
        for e in v.edges.values():
            edge_flag = 1
            cnt_edge += 1
            elb    = int(e.elb)
            to_v   = int(g.vertices[e.to].vlb)
            if (cnt_ver != 1 or cnt_edge != 1):
                query += "      "
            
            query += "(v" + str(vlb - 2)

            if check_list[vid] != 1:
                if (vlb - 2 in neids):
                    query += ":NamedEntity {neid:" + str(vlb - 2) + "})"
                elif (vlb - 2 == NE_CNT):
                    query += ":News)" 
                else:
                    query += ":Word {wid:" + str(vlb - 2) + "})"
                check_list[vid] = 1
            else:
                query += ")"
             
            query += "-[r" + str(edge_id) + ":" + rel_table[elb] + "]->" 
            query += "(v" + str(to_v - 2)
            if check_list[int(e.to)] != 1:
                if (to_v - 2 in neids):
                    query += ":NamedEntity {neid:" + str(to_v - 2) + "})"
                elif (to_v - 2 == NE_CNT):
                    query += ":News)" 
                else:
                    query += ":Word {wid:" + str(to_v - 2) + "})"
                check_list[int(e.to)] = 1
            else:
                query += ")"
            
            if (cnt_edge == num_of_edges) and (cnt_ver == num_ver):
                query += "\n"
            else:
                if not (_check_all_marked(check_list)):
                    query += ", \n" 
                else:
                    query += "\n"
            
            edge_id += 1
    if (edge_flag):
        return_q += ", "
    for i in range(edge_id):
        return_q += 'r' + str(i)
        if (not i == edge_id - 1):
            return_q += ", "

    return (query + return_q)

if __name__ == "__main__":
    # gSpan arguments
    args_str = '-s 11 -d True -l 7 -p False -w False ../data/months/january.gspan.data'
    FLAGS, _ = gSpanParser.parse_known_args(args=args_str.split())
    gs = main(FLAGS)

    frequent_subgraphs = dict()
    support_where = dict() 
    graph_queries = dict()
    print("Graph Count :", len(gs.graphs))

    # Cluster the subgraphs and sample them so that we get single representatives of similar subgraphs
    #gedObj = ged.GraphEditDistance(False, gs.subgraphs, node_subst_cost=2, node_del_cost=2, node_ins_cost=2, reduce_graphs=False)
    #clusters = gedObj.get_clusters(0.1)
    clusters = gohe.get_clusters(gs.subgraphs, 0.9)
    samples = utils.sample_clusters(clusters)

    # Uncomment lines to print the queries
    for sg in gs.subgraphs.values():
    #    print("")
    #    print_graph(sg)
        support_where[sg.gid] = gs.support_where[sg.gid]
    #    print(gSpan2query(sg))
    #    print("")

    # Filter support_where according to samples
    support_where = utils.filter_dict(support_where, samples)
    print("Reduced Subgraph Count :", len(samples))
    print("Mining frequent sequences...")

    # Mine frequent sequences
    freq_seqs = rm.frequentSequences(gs, samples, 3, 7, 1, 1)

    # reID variables, needed because when we run this script for different months, we get same ID's (always starts from 0)
    # But we need them to be different, thus we need to change start_ID and reID them
    subgraphs, samples, freq_seqs, support_where = utils.reID(gs.subgraphs, samples, freq_seqs, support_where, start_ID=0)

    # Mine rules from frequent sequences
    rules = rm.mineRulesFromSequences(freq_seqs, support_where, 0.8)
    
    # Save information mined for a specific month
    utils.save_month(subgraphs=subgraphs, rules=rules, graphs=gs.graphs,
			freq_seqs=freq_seqs, support_where=support_where, name='../data/months/prediction/january')

    # Modify start_ID for next month with the given number
    print("Next month subgraph ID :", max(samples) + 1)
