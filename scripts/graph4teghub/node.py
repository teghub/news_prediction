from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .edge import Edge

DEFAULT_NODE_ID    = -1
DEFAULT_NODE_LABEL = None
DEFAULT_NODE_ATTRS = dict()

class Node(object):
    """
    Node class.
    """
    def __init__(self,
                 nid=DEFAULT_NODE_ID,
                 nlbl=DEFAULT_NODE_LABEL,
                 attrs=DEFAULT_NODE_ATTRS):
        """
        Initializes a Node instance.

        :param nid  : Node id
        :param nlbl : Node Label
        :param attrs: Node attributes
        
        :return     : None 
        """
        self.nid       = nid
        self.nlbl      = nlbl
        self.edges     = dict()
        self.node_attr = attrs

    def add_edge(self, eid, frm, to, elbl, attrs):
        """
        Adds an outgoing edge to node instance.
        
        :param eid  : Edge id 
        :param frm  : Node id of starting point of edge
        :param to   : Node if of end point of edge
        :param elbl : Edge Label
        :param attrs: Edge attributes
        
        :return     : None
        """
        self.edges[to] = Edge(eid, frm, to, elbl, attrs)

    def delete_edge(self, to):
        """
        Deletes an outgoing edge from node instance.
        
        :param to: Node if of end point of edge
        
        :return  : None
        """
        del self.edges[to]
    
    def get_num_edges(self):
        """
        Returns the number of node's edges.

        :return: Edge count of the node
        """
        return len(self.edges)

    def set_attr(self, **attrs):
        """
        Sets or defines attribute-value pairs for node.

        :param **attrs: Attributes as key=value pairs
        
        :return       : None
        """
        for attr, val in attrs.items():
            self.node_attr[attr] = val
    
    def del_attr(self, *attrs):
        """
        Sets or defines attribute-value pairs for node.

        :param *attrs: Attributes (keys) 
        
        :return      : None
        """
        for attr in attrs:
            if (attr in self.node_attr):
                del self.node_attr[attr]