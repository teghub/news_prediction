#! /usr/bin/env python3

# This script is used to extract nodes and relationships in csv form from database

import csv, sys, os, time
from tqdm import tqdm
from py2neo import *

graph     = 0            # Global graph database variable
isOpened  = 0            # Flag for if connection is active or not
path      = os.path.dirname(os.path.abspath(__file__)) + "/../data"
HOST      = 'localhost'
USER      = 'neo4j'      # username for db
PASS      = 'neo4j'      # password for db
PORT      = 7474
BOLT_PORT = 7687
NEWS_CNT  = 0

news_cnt_query = "MATCH (n:News) RETURN COUNT(n.nid)"

nodes_query = ["CALL apoc.export.csv.query('"\
               "MATCH (n:News {nid: ",

               "})-[:CONTAINS]->(w:Word) "\
               "RETURN w.wid as id, w.word as word', '" + path + "/graphs_csv/nodes_",

               ".csv',{})"]

rels_query  = ["CALL apoc.export.csv.query('"\
               "MATCH (n:News {nid: ",

               "})-[:CONTAINS]->(w:Word) "\
               'RETURN n.nid as start_id, w.wid as end_id, 1 as label, "CONTAINS" as type '\
               "UNION "\
               "MATCH (n:News {nid: ",

               "})-[:CONTAINS]->(w:Word)-[:IS]->(ne:NamedEntity) "\
               'RETURN w.wid as start_id, ne.neid as end_id, 2 as label, "IS" as type '\
               "UNION "\
               "OPTIONAL MATCH (w:Word)-[r:FOLLOWED_BY]->(w2:Word) WHERE ",

               " IN r.contained_in "\
               'RETURN w.wid as start_id, w2.wid as end_id, 3 as label, "FOLLOWED_BY" as type'\
               "', '" + path + "/graphs_csv/relationships_",

               ".csv', {})"]

mn_query = 'MATCH (n:News) RETURN n.nid as id, "News" as label '\
           "UNION "\
           'MATCH (ne:NamedEntity) RETURN ne.neid as id, "NamedEntity" as label'

main_nodes_query  = "CALL apoc.export.csv.query('" + mn_query + "', '"
main_nodes_query += path + "/graphs_csv/main_nodes.csv', {})"


# **************** Establishing Database Connection **********************
'''
Database connection is established by Graph function.
Parameters are chosen as host and password. Port is chosen
as default 7687. If port is different than the default, it can be
added as a key-value pair to the function call.
'''
def open_graph_connection(host_name, port, b_port):
    global graph
    global isOpened
    if (isOpened != 1):
        graph = Graph('http://localhost:7474/', auth=(USER, PASS))
        isOpened = 1
        print ("Connection is successfully accomplished to Neo4j Database!")
    else:
        print ("You have already opened a connection!")
# ************************************************************************

if __name__ == "__main__":
    start_time = time.time()

    if not os.path.exists(path + "/graphs_csv"):
        os.makedirs(path + "/graphs_csv")
    
    open_graph_connection(HOST, PORT, BOLT_PORT)

    try:
        print ("Getting news count...")
        NEWS_CNT = int(graph.run(news_cnt_query).evaluate())
    except Exception as e:
        print ("Error while getting news count:", e)
        sys.exit(1)
    else:
        print("Done. # of News:", NEWS_CNT)

    try:
        print("Getting main nodes... (News and Named Entities)")
        main_nodes = graph.run(mn_query).data()
        graph.run(main_nodes_query).evaluate()
    except Exception as e:
        print("Error while getting main nodes:", e)
        sys.exit(1)
    else:
        print("Done.")
    

    for i in tqdm(range(NEWS_CNT)):
        try:
            # Uncomment the line for debugging.
            #print ("Getting nodes of", i + 1, "th News")
            node_query  = nodes_query[0] + str(main_nodes[i]['id']) + nodes_query[1]
            node_query += str(i) + nodes_query[2]
            graph.run(node_query)
        except Exception as e:
            print ("Error while getting nodes of", i + 1, "th News:", e)
            sys.exit(1)
        
        try:
            # Uncomment the line for debugging.
            #print("Getting relationships of", i + 1, "th News")
            rel_query  = rels_query[0] + str(main_nodes[i]['id']) + rels_query[1]
            rel_query += str(main_nodes[i]['id']) + rels_query[2] + str(main_nodes[i]['id'])
            rel_query += rels_query[3] + str(i) + rels_query[4]
            graph.run(rel_query)
        except Exception as e:
            print ("Error while getting relationships of", i + 1, "th News:", e)
            sys.exit(1)
        else:
            # Uncomment the line for debugging.
            #print("Success.")
            pass

    end_time = time.time()
    print("")
    print("Extraction finished in", (end_time - start_time), "seconds.")


