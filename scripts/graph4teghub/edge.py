from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

DEFAULT_EDGE_ID    = -1
DEFAULT_NODE_ID    = -1
DEFAULT_EDGE_LABEL = None
DEFAULT_EDGE_ATTRS = dict()

class Edge(object):
    """
    Edge class.
    """
    def __init__(self,
                 eid=DEFAULT_EDGE_ID,
                 frm=DEFAULT_NODE_ID,
                 to=DEFAULT_NODE_ID,
                 elbl=DEFAULT_EDGE_LABEL,
                 attrs=DEFAULT_EDGE_ATTRS):
        """
        Initializes an Edge instance.

        :param eid  : Edge id
        :param frm  : Node id of starting point of edge
        :param to   : Node if of end point of edge
        :param elbl : Edge Label
        :param attrs: Edge attributes
        
        :return     : None 
        """
        self.eid       = eid
        self.frm       = frm
        self.to        = to
        self.elbl      = elbl
        self.edge_attr = attrs
        
    def set_attr(self, **attrs):
        """
        Sets or defines attribute-value pairs for edge.

        :param **attrs: Attributes as key=value pairs
        
        :return       : None
        """
        for attr, val in attrs.items():
            self.edge_attr[attr] = val
    
    def del_attr(self, *attrs):
        """
        Sets or defines attribute-value pairs for edge.

        :param *attrs: Attributes (keys) 
        
        :return      : None
        """
        for attr in attrs:
            if (attr in self.edge_attr):
                del self.edge_attr[attr]