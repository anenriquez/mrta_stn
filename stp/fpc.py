import logging
import networkx as nx
import copy
from allocation.utils.config_logger import config_logger
import os

""" Achieves full path consistency (fpc) by applying the Floyd Warshall algorithm to the STN"""


def get_minimal_network(stn):
    code_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(code_dir)
    config_logger(main_dir + '/config/logging.yaml')
    logger = logging.getLogger('stp.fpc')
    minimal_network = copy.deepcopy(stn)

    shortest_path_array = nx.floyd_warshall(stn)
    if stn.is_consistent(shortest_path_array):
        # Get minimal stn by updating the edges of the stn to reflect the shortest path distances
        minimal_network.update_edges(shortest_path_array)
        return minimal_network
    else:
        logger.error("The minimal network is inconsistent")
