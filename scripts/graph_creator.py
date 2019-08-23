#!/usr/bin/env python3

# This script is used to import the csv files to the graph database
# Go to line 66 for csv file names

import time, csv, sys, os, subprocess, shutil
from shutil import copyfile
from py2neo import Node, Relationship, Graph, NodeMatcher
from tqdm import tqdm, trange

datafile_path = "../data/"

graph    = 0            # Global graph database variable
isOpened = 0            # Flag for if connection is active or not
HOST     = 'localhost'
PORT     = 7474
BOLT_PORT= 7687

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
        # Change auth here if needed (username:password)
        graph = Graph('http://localhost:7474/', auth=('neo4j','neo4j'))
        isOpened = 1
        print ("Connection is successfully accomplished to Neo4j Database!")
    else:
        print ("You have already opened a connection!")
# ************************************************************************

# ************************* Importing Data ******************************

if (__name__ == "__main__"):
    start_time = time.time()

    database_name = "CALL dbms.listConfig('dbms.active_database') YIELD value"
    data_dir      = "CALL dbms.listConfig('dbms.directories.data') YIELD value"
    import_dir    = "CALL dbms.listConfig('dbms.directories.import') YIELD value"

    # csv files
    node_files = [datafile_path + 'news.csv',
		  datafile_path + 'words.csv',
		  datafile_path + 'named_entities.csv']
    rel_files  = [datafile_path + 'wwr.csv',
		  datafile_path + 'nwr.csv',
		  datafile_path + 'newr.csv']

    open_graph_connection(HOST, PORT, BOLT_PORT)
    print ("Clearing all data in the Neo4j database.")

    import_dir    = graph.run(import_dir).evaluate()
    bin_dir       = import_dir[:-6] + "bin"
    data_dir      = graph.run(data_dir).evaluate()
    database_name = graph.run(database_name).evaluate()

    if (os.path.exists(data_dir + "/databases/" + database_name)):
        shutil.rmtree(data_dir + "/databases/" + database_name, ignore_errors=True)

    args           ="./neo4j-admin import "\
                    "--database=" + str(database_name)+ " "\
                    "--id-type=INTEGER "
    for node in node_files:
        args += "--nodes=../import/" + node + " "
    for rel in rel_files:
        args += "--relationships=../import/" + rel + " "
    args += "--multiline-fields=true"

    args           = args.split()
    restart_server ="./neo4j restart".split()

    print ("Copying CSV files to import directory of the Neo4j Database.")
    for node_file in node_files:
        copyfile("./" + node_file, str(import_dir) + "/" + node_file)
    for rel_file in rel_files:
        copyfile("./" + rel_file, str(import_dir) + "/" + rel_file)
    print ("Copy process is completed. Adjusting index properties.\n")

    print ("Import operation is starting...")
    popen = subprocess.Popen(args, cwd=bin_dir , stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    for line in str(output).split("\\n")[-7:]:
        if (line.startswith("b'")):
            print (line[2:])
        elif not (len(line) == 1 and line == "'"):
            print (line)
    print ("\n")
    popen = subprocess.Popen(restart_server, cwd=bin_dir , stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    for line in str(output).split("\\n"):
        if (line.startswith("b'")):
            print (line[2:])
        elif not (len(line) == 1 and line == "'"):
            print (line)

    print ("Deleting copied CSV files from import directory...")
    for node_file in node_files:
        print ("Deleting " + import_dir + "/" + node_file)
        os.remove(import_dir + "/" + node_file)
    for rel_file in rel_files:
        print ("Deleting " + import_dir + "/" + rel_file)
        os.remove(import_dir + "/" + rel_file)

    print ("Files are deleted.")
    end_time = time.time()

    print ("\n----> Result <----")
    print ("Transfer operation is completed!")
    if (((end_time - start_time)/60) > 1.0):
        print ("Total passed time is %f minutes"%((end_time - start_time)/60))
    else:
        print ("Total passed time is %f seconds"%(end_time - start_time))
