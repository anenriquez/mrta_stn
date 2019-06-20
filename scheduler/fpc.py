import copy
import logging
import networkx as nx

from scheduler.temporal_networks.stn import STN

""" Achieves full path consistency (fpc) by applying the Floyd Warshall algorithm to the STN"""


def get_minimal_network(stn):
    logger = logging.getLogger('scheduler.fpc')

    shortest_path_array = nx.floyd_warshall(stn)
    if stn.is_consistent(shortest_path_array):
        # Get minimal stn by updating the edges of the stn to reflect the shortest path distances
        stn.update_edges(shortest_path_array)
        return stn
    else:
        logger.error("The minimal network is inconsistent")
