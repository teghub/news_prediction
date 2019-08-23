from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import csv
import json
import itertools
import collections
from tqdm import tqdm
from .node import Node
from networkx.drawing.nx_agraph import graphviz_layout

DEFAULT_GRAPH_ID    = -1
DEFAULT_EXPORT_PATH = os.path.join(os.getcwd(), "output")

sys.path.insert(0, os.path.join(os.getcwd(), '..'))

class Graph(object):
    """
    Graph class.
    
    The implementation is inspired by the gSpan Graph implementation.
    
    To check out the gSpan project, please go to the following link:
    https://github.com/betterenvi/gSpan
    """
    def __init__(self,
                 gid=DEFAULT_GRAPH_ID,
                 is_directed=True,
                 eid_auto_increment=True,
                 export_path=DEFAULT_EXPORT_PATH
                 ):
        """
        Initializes a Graph instance.

        :param gid               : Graph id
        :param is_directed       : Flag, if graph is directed or not
        :param eid_auto_increment: Flag, if increment edge ids automatically

        :return                  : None
        """
        self.gid                = gid
        self.nodes              = dict()
        self.counter            = itertools.count()
        self.graph_attrs        = dict()
        self.set_of_nlbl        = collections.defaultdict(set)
        self.set_of_elbl        = collections.defaultdict(set)
        self.is_directed        = is_directed
        self.export_path        = export_path
        self.eid_auto_increment = eid_auto_increment

    def get_attributes(self):
        """
        Returns the attributes in the graph.

        :return: Keys of the attributes
        """
        return self.graph_attrs.keys()

    def get_num_nodes(self):
        """
        Returns the number of nodes in the graph.

        :return: Number of nodes
        """
        return len(self.nodes)

    def get_num_label_edges(self, elbl):
        """
        Returns the number of edges which has the given label.

        :param elbl: Edge label

        :return    : Number of edges with that label
        """
        if not (elbl in self.set_of_elbl):
            return 0
        return len(self.set_of_elbl[elbl])
    
    def get_num_label_nodes(self, nlbl):
        """
        Returns the number of nodes which has the given label.

        :param nlbl: Node label

        :return    : Number of nodes with that label
        """
        if not (nlbl in self.set_of_nlbl):
            return 0
        return len(self.set_of_nlbl[nlbl])
    
    def add_node(self, nid, nlbl, **attrs):
        """
        Adds a node to the graph.

        :param nid : Node id
        :param nlbl: Node label

        :return    : Graph object itself
        """
        if (nid in self.nodes):
            return self
        self.nodes[nid] = Node(nid, nlbl, attrs)
        self.set_of_nlbl[nlbl].add(nid)
        return self

    def add_edge(self, eid, frm, to, elbl, **attrs):
        """
        Adds an edge to the graph.

        :param eid : Edge id
        :param frm : Node id of starting point of edge
        :param to  : Node if of end point of edge
        :param elbl: Edge Label
        
        :return    : Graph object itself 
        """
        if (frm in self.nodes and
            to in self.nodes and
            to in self.nodes[frm].edges):
            return self
        
        if (self.eid_auto_increment):
            eid = next(self.counter)
        
        self.nodes[frm].add_edge(eid, frm, to, elbl, attrs)
        self.set_of_elbl[elbl].add((frm, to))

        if not (self.is_directed):
            self.nodes[to].add_edge(eid, to, frm, elbl, attrs)
            self.set_of_elbl[elbl].add((to, frm))
        return self

    def display(self):
        """
        Displays the graph in a text format.

        :return: None
        """
        print('ObjType ID1 ID2 Label AvailableAttrs')
        print('G {} # # {}'.format(self.gid, self.get_attributes))
        for nid in self.nodes:
            print('N {} # {} {}'.format(nid, 
                                        self.nodes[nid].nlbl, 
                                        self.nodes[nid].node_attr))
        for frm in self.nodes:
            node_edges = self.nodes[frm].edges
            for to in node_edges:
                if not (self.is_directed):
                    if frm < to:
                        print('E {} {} {} {}'.format(frm, to, node_edges[to].elbl,
                                                     node_edges[to].edge_attr.keys()))
                else:
                    print('E {} {} {} {}'.format(frm, to, node_edges[to].elbl,
                                                     node_edges[to].edge_attr.keys()))
        print("")
        print("-"* 40)

    def plot(self):
        """
        Visualize the graph by using networkx and matplotlib.pyplot.

        :return: None
        """
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
        except Exception as e:
            print('Can not plot graph {}: {}'.format(self.gid, e))
            return
        elbls    = {}
        nlbls    = {nid: node.nlbl for nid, node in self.nodes.items()}
        nx_graph = nx.DiGraph() if self.is_directed else nx.Graph()
        for nid, node in self.nodes.items():
            nx_graph.add_node(nid, label=node.nlbl)
        for nid, node in self.nodes.items():
            for to, edge in node.edges.items():
                if (self.is_directed) or (nid < to):
                    nx_graph.add_edge(nid, to, label=edge.elbl)
                    elbls[(nid, to)] = "type: " + str(edge.elbl)
        figsize = (min(20, 1 * len(self.nodes)),
                   min(20, 1 * len(self.nodes)))
        pos = graphviz_layout(nx_graph, 'dot')
        plt.figure(self.gid, figsize=figsize)
        plt.title("Graph " + str(self.gid))
        nx.draw(nx_graph, pos=pos, arrows=True, with_labels=True, labels=nlbls, 
                node_color='lightblue', font_color='black', edge_color='grey', alpha=0.9, node_size=700)
        nx.draw_networkx_edge_labels(nx_graph, pos=pos, edge_labels=elbls, font_color='black')
        plt.axis('off')
        plt.show()

    def load_graph_attrs(self, graph_attrs_path='graph_0.attrs'):
        """
        Loads graph attributes from a attribute file.

        Attribute file consists of an dictionary object in string format.

        :param graph_attrs_path: Attribute file path
        
        :return                : If success 1, else -1
        """
        if (not graph_attrs_path or
            not os.path.exists(graph_attrs_path)):
            print("Cannot load attributes to graph object:", self.gid)
            return -1
        with open(graph_attrs_path, 'r') as gaf:
            try:
                self.graph_attrs = eval(gaf.read())
            except Exception as e:
                print("Cannot load attributes to graph object:", self.gid, "-", e)
                return -1
        return 1
    
    def create_from_gSpanObj(self, gSpanObj):
        if not gSpanObj:
            print("Please give an existing gSpan Object.")
            return -1
        try:
            import gspan_mining
            self.gid = int(gSpanObj.gid)
            for vertex in gSpanObj.vertices.values():
                self.add_node(nid=int(vertex.vid), nlbl=vertex.vlb)
                for edge in vertex.edges.values():
                    self.add_edge(eid=int(edge.eid), frm=int(edge.frm), 
                                  to=int(edge.to), elbl=edge.elb)
            return 1
        except Exception as e:
            print("Error while transforming gSpan Object to graph format:", e)
            return -1
        return 1

    def get_OneHotEncoding(self, vocab=[]):
        if not vocab:
            print("Please give an existing vocabulary list.")
            return None
        try:
            import numpy as np
            o_h_encoding = np.zeros(shape=(len(vocab),))
            for i in range(len(vocab)):
                word = vocab[i]
                if word in self.set_of_nlbl:
                    o_h_encoding[i] = 1
            return o_h_encoding
        except Exception as e:
            print("Error while getting One Hot Encoding of Graph {}:".format(self.gid), e)
            return None
        

    def convert_networkx(self):
        """
        Transform graph to a networkx graph object.

        :return: Networkx Graph Object
        """
        try:
            import networkx as nx
        except Exception as e:
            print('Can not convert graph {}: {}'.format(self.gid, e))
            return None
        nx_graph = nx.DiGraph() if self.is_directed else nx.Graph()
        for nid, node in self.nodes.items():
            nx_graph.add_node(nid, **node.node_attr)
        for nid, node in self.nodes.items():
            for to, edge in node.edges.items():
                if (self.is_directed) or (nid < to):
                    nx_graph.add_edge(nid, to, **edge.edge_attr)
        return nx_graph

    def export_for_HOPE(self):
        """
        Exports the graph to HOPE edgelist format.

        Output File consists of edges:
        ...
        frm1 to1
        frm2 to2
        frm3 to3
        ...

        :return: None
        """
        try:
            graph_id    = self.gid
            EXPORT_PATH = os.path.join(self.export_path, "HOPE")
            if not (os.path.exists(self.export_path)):
                os.makedirs(self.export_path)
            if not (os.path.exists(EXPORT_PATH)):
                os.makedirs(EXPORT_PATH)
            with(open(os.path.join(EXPORT_PATH, str(graph_id) + ".edgelist"), "w+")) as f:
                for n in tqdm(self.nodes.values(), desc="Graph {} to HOPE edgelist".format(graph_id)):
                    for e in n.edges.values():
                        f.write(str(e.frm) + " " + str(e.to) + "\n")
            with(open(os.path.join(EXPORT_PATH, str(graph_id) + ".labels"), "w+")) as f:
                nodes_lbls = []
                for n in self.nodes.values():
                    nodes_lbls.append(n.nlbl)
                f.write(" ".join(nodes_lbls))

        except Exception as e:
            print("Error while exporting Graph {} to HOPE edgelist format: {}".format(self.gid, e))
            return

    def export_for_DeepWalk(self):
        """
        Exports the graph adj matrix format for DeepWalk.

        Output File consists of edges:
        ...
        frm1 to1 to2 to3 to4 to5
        frm2 to4 to7 to3 to2
        frm3 to5
        ...

        :return: None
        """
        try:
            graph_id    = self.gid
            EXPORT_PATH = os.path.join(self.export_path, "DeepWalk")
            if not (os.path.exists(self.export_path)):
                os.makedirs(self.export_path)
            if not (os.path.exists(EXPORT_PATH)):
                os.makedirs(EXPORT_PATH)
            with(open(os.path.join(EXPORT_PATH, str(graph_id) + ".adj"), "w+")) as f:
                for n in tqdm(self.nodes.values(), desc="Graph {} to DeepWalk".format(graph_id)):
                    f.write(str(n.nid))
                    for e in n.edges.values():
                        f.write(" " + str(e.to))
                    f.write("\n")
        except Exception as e:
            print("Error while exporting Graph {} to DeepWalk format: {}".format(self.gid, e))
            return

    def export_for_graph2vec(self):
        """
        Exports the graph in the JSON format for graph2vec.

        Output File consists of edges and nodes:
        -> Edges          : list of lists, ex. [[frm, to], [frm, to]]
        -> Nodes(Features): Key-Value Pairs, ex. {id: label, id: label}

        :return: None
        """
        try:
            EXPORT_PATH = os.path.join(self.export_path, "graph2vec")
            if not (os.path.exists(self.export_path)):
                os.makedirs(self.export_path)
            if not (os.path.exists(EXPORT_PATH)):
                os.makedirs(EXPORT_PATH)
            edges      = []
            features   = {}
            graph_dict = {}
            graph_id   = self.gid
            for n in tqdm(self.nodes.values(), desc="Graph {} to graph2vec".format(graph_id)):
                if (str(n.nid) not in features):
                    features[str(n.nid)] = str(n.nlbl)
                for e in n.edges.values():
                    edges.append([e.frm, e.to])
            graph_dict["edges"]    = edges
            graph_dict["features"] = features
            with(open(os.path.join(EXPORT_PATH, str(graph_id) + ".json"), "w+")) as f:
                f.write(json.dumps(graph_dict))
        except Exception as e:
            print("Error while exporting Graph {} to graph2vec JSON format: {}".format(self.gid, e))
            return
    
    def delete_graph2vec_json(self):
        """
        Deletes the JSON file created as graph2vec input.

        :return: None
        """
        try:
            EXPORT_PATH = os.path.join(self.export_path, "graph2vec")
            filename = os.path.join(EXPORT_PATH, str(self.gid) + ".json")
            if (os.path.exists(filename)):
                os.remove(filename)
        except Exception as e:
            print("Error while deleting the graph2vec export of Graph {}: {}".format(self.gid, e))
            return

    def import_from_csv(self, nodes_file_path=None, relationships_file_path=None, has_common_id=True, delimiter=','):
        """
        Imports graph structure from a nodes and a relationships file.

        File Structures should be as the following:
        -> Nodes File:
            -> Headers must include either 'id' or 'label'
               If 'label' field is wanted to be used as node label
               has_common_id parameter should be given as False.
            -> Any other field and its values will be added as node attribute.
        
        ->Relationships File:
            -> Headers must include 'start_id', 'label' and 'end_id'
               If Graph is defined as eid_auto_increment=True, there is no need for
               including 'eid' field in the headers. It is optional.
               Else, there should exists a 'eid' field o.w. Exception can raise.
            -> Any other field and its values will be added as edge attribute.

        :param nodes_file_path        : CSV file that contains nodes.
        :param relationships_file_path: CSV file that contains relationships.
        :param has_common_id          : If the ids are unique and common between several different graph files.
        :param delimiter              : Delimiter character for the files

        :return                       : None
        """
        if not (nodes_file_path and relationships_file_path):
            raise Exception("Please give nodes and relationships files as parameters.")
        if (not os.path.exists(nodes_file_path) 
                or 
            not os.path.exists(relationships_file_path)):
            raise Exception("Nodes or relationships files don't exists.")
        node_id = dict()
        with open(nodes_file_path, 'r') as node_file:
            node_headers = node_file.readline().strip().replace('"', "")
            node_headers.replace("'", "")
            node_headers = node_headers.split(delimiter)
            if (not self._check_headers(node_headers, 0)):
                raise Exception("Please check that nodes file header contains one of the 'id' or 'label' fields.")
            nid        = itertools.count()
            nlbl       = None
            node_csv   = csv.DictReader(node_file, fieldnames=node_headers)
            for node in node_csv:
                _id           = next(nid)
                nlbl          = node['id'] if (('id' in node) and has_common_id) else node['label']
                node_attrs    = self._get_attributes_from_headers(node, node_headers, 0)
                node_id[int(nlbl)] = int(_id)
                self.add_node(_id, nlbl, **node_attrs)
            
        with open(relationships_file_path, 'r') as rel_file:
            rel_headers = rel_file.readline().strip().replace('"', "")
            rel_headers.replace("'", "")
            rel_headers = rel_headers.split(delimiter)
            if (not self._check_headers(rel_headers, 1)):
                raise Exception("Please check that relationships file header contains" \
                                "'start_id', 'label' and 'end_id' or 'eid' fields.")
            eid     = itertools.count()
            elbl    = None
            rel_csv = csv.DictReader(rel_file, fieldnames=rel_headers)
            for rel in rel_csv:
                try:
                    to         = node_id[int(rel['end_id'])]
                    frm        = node_id[int(rel['start_id'])]
                    elbl       = rel['label']
                    edge_attrs = self._get_attributes_from_headers(rel, rel_headers, 1)
                    self.add_edge(int(next(eid)), frm, to, elbl, **edge_attrs)
                except Exception as e:
                    print("\n\n")
                    print("-" * 20)
                    print("Cannot create relationship:", e)
                    print("Passed this relationship.")
                    print(relationships_file_path)
                    print("-" * 20)
                    print("\n\n")
                    continue
    
    def _get_attributes_from_headers(self, obj, headers, type_flag):
        """
        Extracts and returns the attributes from the object.

        :param obj      : It is a node or edge object
        :param headers  : Headers of the object
        :param type_flag: Defines the object type (0->Node, 1->Edge)

        :return         : Objects' attributes as dictionary 
        """
        if not headers:
            return dict()
        attrs  = dict()
        fields = None
        if not type_flag:
            fields = list(set(headers) - set(['id', 'label']))
        else:
            fields = list(set(headers) - set(['start_id' , 'label', 'end_id']))
            if (not self.eid_auto_increment):
                fields.append('eid')
        for key in fields:
            attrs[key] = obj[key]
        return attrs

    def _check_headers(self, headers, type_flag):
        """
        Checks if the file has the required header fields.

        :param headers  : Headers of the given file
        :param type_flag: Defines the object type (0->Node, 1->Edge)

        :return         : 0->Lack of Header, 1->Sufficient
        """
        if not headers:
            return 0
        if not type_flag:
            node_headers = ['id', 'label']
            for lbl in node_headers:
                if lbl in headers:
                    return 1
            return 0
        else:
            edge_headers = ['start_id' , 'label', 'end_id']
            if (not self.eid_auto_increment):
                edge_headers.append('eid')
            for lbl in edge_headers:
                if lbl not in headers:
                    return 0
            return 1
