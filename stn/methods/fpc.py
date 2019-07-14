import logging
import networkx as nx
import copy
from stn.utils.config_logger import config_logger
from pathlib import Path

""" Achieves full path consistency (fpc) by applying the Floyd Warshall algorithm to the STN"""


def get_minimal_network(stn):

    p = Path(__file__).parents[2]
    config_logger(str(p) + '/config/logging.yaml')
    logger = logging.getLogger('stn.fpc')
    minimal_network = copy.deepcopy(stn)

    shortest_path_array = nx.floyd_warshall(stn)
    if stn.is_consistent(shortest_path_array):
        # Get minimal stn by updating the edges of the stn to reflect the shortest path distances
        minimal_network.update_edges(shortest_path_array)
        return minimal_network
    else:
        logger.error("The minimal network is inconsistent")
