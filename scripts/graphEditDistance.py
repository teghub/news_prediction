#! /usr/bin/env python3

# Adding gSpan Mining Library to path
import sys, os
CURR_PATH = os.getcwd()
sys.path.insert(0, os.path.join(CURR_PATH, 'gSpan'))

# Other Libraries
import networkx as nx
from tqdm import tqdm
import pickle, time, gspan_mining
import multiprocessing as mp
from networkx.algorithms.similarity import graph_edit_distance as ged
from networkx.algorithms.similarity import optimize_graph_edit_distance as oged

class GraphEditDistance:
    def __init__(self, is_optimized=False, graphs=None, graph_file_path=None, with_pooling=True,
                 node_subst_cost=2, node_del_cost=2, node_ins_cost=2,
                 edge_subst_cost=1, edge_del_cost=1, edge_ins_cost=1, reduce_graphs=False):
        if (not graphs) and (not graph_file_path):
            raise Exception("Please give list of graphs as a first parameter or graph file path as second parameter.")
        self.graph_count       = 0                # Total number of initial graphs
        self.rdc_graph_count   = 0                # Total number of reduced graphs
        self.average_ged       = 0.0              # Average GDE of ALL graphs
        self.graphs            = []               # Given Graphs
        self.reduced_graphs    = []               # Reduced Graphs
        self.reduced_graph_ids = []               # Graph ID's of Reduced Graphs
        self.graphs_avg_ged    = []
        self.is_optimized      = is_optimized     # Flag for Optimized GED algorithm
        self.node_del_cost     = node_del_cost    # Node deletion cost
        self.node_ins_cost     = node_ins_cost    # Node insertion cost
        self.node_subst_cost   = node_subst_cost  # Node substitution cost
        self.edge_del_cost     = edge_del_cost    # Edge deletion cost
        self.edge_ins_cost     = edge_ins_cost    # Edge insertion cost
        self.edge_subst_cost   = edge_subst_cost  # Edge substitution cost
        self.graph_file_path   = graph_file_path  # Graph File path incase of loading
        self.edge_table        = {                # Label to Edge Conversion
            1: "CONTAINS",
            2: "IS",
            3: "FOLLOWED_BY" 
        }

        if not (graphs):                          # Given graphs
            self.graphs = []
        else:
            self._parse_graph(graphs)

        if (self.graph_file_path):                # Given graph file path
            self.parse_graph_from_file()
        
        self.graph_count += len(self.graphs)
        print(self.graph_count, "graphs are imported.")
        print("-" * 30)
        if (reduce_graphs):
            if (with_pooling):
                self._get_average_ged_with_pool()
            else:
                self._get_average_ged()
            self._reduce_graphs()
    ########################################################################

    ######################### General Functions ############################
    def graph_edit_distance(self, G1, G2):
        """
        Returns the graph edit distance between G1 and G2
        """
        if not (self.is_optimized):
            return ged(G1, G2, 
                    node_match=self._node_match, edge_match=self._edge_match,
                    node_subst_cost=self._node_subst_cost, node_del_cost=self._node_del_cost, 
                    node_ins_cost=self._node_ins_cost, 
                    edge_subst_cost=self._edge_subst_cost, edge_del_cost=self._edge_del_cost, 
                    edge_ins_cost=self._edge_ins_cost)
        else:
            minv = 0.0
            for v in oged(G1, G2, 
                        node_match=self._node_match, edge_match=self._edge_match,
                        node_subst_cost=self._node_subst_cost, node_del_cost=self._node_del_cost, 
                        node_ins_cost=self._node_ins_cost, 
                        edge_subst_cost=self._edge_subst_cost, edge_del_cost=self._edge_del_cost, 
                        edge_ins_cost=self._edge_ins_cost):
                minv = v
            return minv

    def print_graph(self, graph):
        """
        Prints graph.
        """
        print("GID  :", graph.graph['id'])
        print("Nodes:", graph.nodes)
        print("NodeI:", [graph.node[i]['id'] for i in range(len(graph.node))])
        print("Edges:", graph.edges)
        print("EdgeI:", [graph[u][v]['weight'] for u, v in graph.edges])
        print("EdgeL:", [self.edge_table[graph[u][v]['weight']] for u, v in graph.edges])
        print("-" * 30)

    def get_clusters(self, ged_ratio=0.2):
        """
        Returns clusters.
        """
        clusterid = 0
        i = 0
        graphs = []
        assigned_clusters_dict = {}
        graphs = self.reduced_graphs if self.reduced_graphs else self.graphs

        for graph in tqdm(graphs, desc="Clustering"):
            if graph.graph['id'] in assigned_clusters_dict:
                continue
            distances = {}
            for j  in range(i, len(graphs)):
                othergraph = graphs[j]
                distances[othergraph.graph['id']] = self.graph_edit_distance(othergraph, graph)
            threshold = ged_ratio * (len(graph.nodes)*self.node_ins_cost + len(graph.edges)*self.edge_ins_cost)
            for k, v in distances.items():
                if v <= threshold:
                    assigned_clusters_dict[k] = clusterid
            clusterid += 1
        clusters = {}
        for k, v in assigned_clusters_dict.items():
            if v in clusters:
                clusters[v].append(k)
            else:
                clusters[v] = [k]

        return clusters
    ########################################################################

    ##################### Convert 2 NetworkX Graph #########################
    def graph2nxGraph(self, graph):
        """
        Creates a networkx representation of a gSpan graph
        """
        try:
            edges = []
            nodes = {}
            GRAPH = nx.DiGraph(id=int(graph.gid))
            for vertex in graph.vertices.values():
                if (int(vertex.vid) not in nodes):
                    GRAPH.add_node(int(vertex.vid))
                    GRAPH.nodes[int(vertex.vid)]['id'] = int(vertex.vlb)
                for edge in vertex.edges.values():
                    edges.append((int(edge.frm), int(edge.to), int(edge.elb)))
            GRAPH.add_weighted_edges_from(edges)
            return GRAPH
        except Exception as e:
            print("Error while transforming subgraph to nx graph format:", e)
            return None
    ########################################################################

    ########################## Parsing Graph ###############################
    def _parse_graph(self, graphs):
        """
        Parses graph from self.graph_file_path file.
        """
        try:
            print("Transforming graphs...")
            for graph in tqdm(graphs.values(), desc="Graph2nxGraph"):
                nxgraph = self.graph2nxGraph(graph)
                if (nxgraph):
                    self.graphs.append(nxgraph)
            print("-" * 60)
        except Exception as e:
            print("Error while reading subgraph file:", e)
            return

    def parse_graph_from_file(self):
        """
        Parses graph from self.graph_file_path file.
        """
        try:
            if not (self.graph_file_path):
                raise Exception("Please give graph path as the second parameter.")
            print("Reading graphs from file and transforming them...")
            with (open(self.graph_file_path, "rb")) as f:
                subgraphs = pickle.loads(f.read())
                for graph in tqdm(subgraphs.values(), desc="FileGraph2nxGraph"):
                    nxgraph = self.graph2nxGraph(graph)
                    if (nxgraph):
                        self.graphs.append(nxgraph)
                print("-" * 60)
        except Exception as e:
            print("Error while reading subgraph file:", e)
            return
    ########################################################################

    ####################### Normal Behaviour ###############################
    def _reduce_graphs(self):
        """
        Reduces graphs according to the total average gde in graphs
        """
        st = time.time()
        self.reduced_graphs    = []
        self.reduced_graph_ids = []
        for gindex in tqdm(range(len(self.graphs_avg_ged)), desc="Reducing Graphs"):
            if (self.graphs_avg_ged[gindex] >= self.average_ged):
                self.reduced_graphs.append(self.graphs[gindex])
                self.reduced_graph_ids.append(self.graphs[gindex].graph['id'])
        self.rdc_graph_count = len(self.reduced_graphs)
        et = time.time()
        print("Reducing resulted with", self.rdc_graph_count, "graphs.")
        print("Time:", (et-st))
        print("-" * 30)

    def _get_average_ged(self):
        """
        Calculates the average gde value for all graphs and indivudial graphs
        """
        st = time.time()
        print("Getting average graph edit distance...")
        total_ged           = 0.0
        self.graphs_avg_ged = []
        for graph1 in tqdm(self.graphs, desc="Avg Dist"):
            graph_ged = 0.0
            for graph2 in self.graphs:
                graph_ged += self.graph_edit_distance(graph1, graph2)
            graph_ged  = graph_ged / self.graph_count
            total_ged += graph_ged
            self.graphs_avg_ged.append(graph_ged)
        self.average_ged = total_ged / self.graph_count
        et = time.time()
        print("Average Graph Edit Distance:", self.average_ged)
        print("Time:", (et-st))
        print("-" * 30)
    ########################################################################

    ####################### Pooling Behaviour ##############################    
    def _get_graph_ged(self, graph):
        """
        Returns the average ged value for a specific graph.
        """
        graph_ged = 0.0
        for graph2 in tqdm(self.graphs, desc="Avg Dist with Pooling"):
            graph_ged += self.graph_edit_distance(graph, graph2)
        graph_ged = graph_ged / self.graph_count
        return graph_ged

    def _get_average_ged_with_pool(self):
        """
        Calculates the average gde value for all graphs and indivudial graphs
        by using Multiprocessing.
        """
        st = time.time()
        print("Getting average graph edit distance with Multiprocessing Pool...")
        self.average_ged = 0.0
        with mp.Pool(os.cpu_count()) as p:
            self.graphs_avg_ged = p.map(self._get_graph_ged, self.graphs)
        self.average_ged = sum(self.graphs_avg_ged) / self.graph_count
        et = time.time()
        print("Average Graph Edit Distance:", self.average_ged)
        print("Time:", (et-st))
        print("-" * 30)
    ########################################################################

    ########################## Cost Functions ##############################
    def _node_match(self, n1, n2):
        """
        Node matching procedure
        """
        if not (('id' in n1) and ('id' in n2)):
            return False
        if (n1['id'] == n2['id']):
            return True
        return False

    def _edge_match(self, e1, e2):
        """
        Edge matching procedure
        """
        if not (('weight' in e1) and ('weight' in e2)):
            return False
        if (e1['weight'] == e2['weight']):
            return True
        return False

    def _node_subst_cost(self, n1, n2):
        """
        Node substitution cost procedure
        """
        if (n1['id'] == n2['id']):
            return 0
        return self.node_subst_cost
    
    def _node_del_cost(self, n1):
        """
        Node deletion cost procedure
        """
        return self.node_del_cost
    
    def _node_ins_cost(self, n1):
        """
        Node insertion cost procedure
        """
        return self.node_ins_cost

    def _edge_subst_cost(self, e1, e2):
        """
        Edge substitution cost procedure
        """
        if (e1['weight'] == e2['weight']):
            return 0
        return self.edge_subst_cost
    
    def _edge_del_cost(self, e1):
        """
        Edge deletion cost procedure
        """
        return self.edge_del_cost
    
    def _edge_ins_cost(self, e1):
        """
        Edge insertion cost procedure
        """
        return self.edge_ins_cost
    ########################################################################

# You can use the main function for the testing purposes
def main():    
    print("-" * 60)
    et = time.time()
    graphs = GraphEditDistance(False, None, os.path.join(CURR_PATH, "subgraphs777.pickle"), with_pooling=True)
    st = time.time()
    print("Time:", (st-et))
    print("")
    print("-" * 60)
    et = time.time()
    graphs2 = GraphEditDistance(False, None, os.path.join(CURR_PATH, "subgraphs777.pickle"), with_pooling=False)
    st = time.time()
    print("Time:", (st-et))
    """counter = 0
    for graph1 in graphs.reduced_graphs:
        print("Average Graph Edit Distance of Graph", graph1.graph['id'], "=", graphs.graphs_avg_ged_n[counter])
        print("Average Graph Edit Distance (Pool) of Graph", graph1.graph['id'], "=", graphs.graphs_avg_ged[counter])
        print("")
        for graph2 in graphs.reduced_graphs:
            print("Graph 1:", graph1.graph['id'], "- Graph 2:", graph2.graph['id'])
            print("GraphEditDistance:", graphs.graph_edit_distance(graph1, graph2))
            print("-" * 30)
            graphs.print_graph(graph1)
            graphs.print_graph(graph2)
            input("Press Enter to Continue...")
            print("")
        counter += 1"""
    

if (__name__ == "__main__"):
    main()
