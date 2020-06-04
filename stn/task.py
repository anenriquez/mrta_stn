from stn.utils.as_dict import AsDictMixin


class Edge(AsDictMixin):
    def __init__(self, name, mean, variance, **kwargs):
        self.name = name
        self.mean = round(mean, 3)
        self.variance = round(variance, 3)
        self.standard_dev = round(variance ** 0.5, 3)

    def __str__(self):
        to_print = ""
        to_print += "{}: N({}, {})".format(self.name, self.mean, self.standard_dev)
        return to_print

    def __sub__(self, other):
        # Difference of two independent random variables
        mean = self.mean - other.mean
        variance = self.variance + other.variance
        return mean, variance

    def __add__(self, other):
        # Addition of two independent random variables
        mean = self.mean + other.mean
        variance = self.variance + other.variance
        return mean, variance


class Timepoint(AsDictMixin):
    """
        r_earliest_time (float): earliest time relative to a ztp
        r_latest_time (float): latest time relative to a ztp

    """
    def __init__(self, name, r_earliest_time, r_latest_time, **kwargs):
        self.name = name
        self.r_earliest_time = round(r_earliest_time, 3)
        self.r_latest_time = round(r_latest_time, 3)

    def __str__(self):
        to_print = ""
        to_print += "{}: [{}, {}]".format(self.name, self.r_earliest_time, self.r_latest_time)
        return to_print


class Task(AsDictMixin):
    def __init__(self, task_id, timepoints, edges, pickup_action_id, delivery_action_id):

        """ Constructor for the Task object

        Args:
            task_id (UUID): An instance of an UUID object
            timepoints (list): list of timepoints (Timepoints)
            Edges (list): list of edges (Edges)
            pickup_action_id (UUID): Action id of the pickup action
            delivery_action_id (UUID): Action id of te delivery action
        """
        self.task_id = task_id
        self.timepoints = timepoints
        self.edges = edges
        self.pickup_action_id = pickup_action_id
        self.delivery_action_id = delivery_action_id

    def __str__(self):
        to_print = ""
        to_print += "{} \n".format(self.task_id)
        to_print += "Timepoints: \n"
        for timepoint in self.timepoints:
            to_print += str(timepoint) + "\t"
        to_print += "\n Edges: \n"
        for edge in self.edges:
            to_print += str(edge) + "\t"
        to_print += "\n Pickup action:" + str(self.pickup_action_id)
        to_print += "\n Delivery action:" + str(self.delivery_action_id)
        return to_print

    def get_timepoint(self, timepoint_name):
        for timepoint in self.timepoints:
            if timepoint.name == timepoint_name:
                return timepoint

    def get_edge(self, edge_name):
        for edge in self.edges:
            if edge.name == edge_name:
                return edge

    def update_timepoint(self, timepoint_name, r_earliest_time, r_latest_time=float('inf')):
        in_list = False
        for timepoint in self.timepoints:
            if timepoint.name == timepoint_name:
                in_list = True
                timepoint.r_earliest_time = r_earliest_time
                timepoint.r_latest_time = r_latest_time
        if not in_list:
            self.timepoints.append(Timepoint(timepoint_name, r_earliest_time, r_latest_time))

    def update_edge(self, edge_name, mean, variance):
        in_list = False
        for edge in self.edges:
            if edge.name == edge_name:
                in_list = True
                edge.mean = round(mean, 3)
                edge.variance = round(variance, 3)
                edge.standard_dev = round(variance ** 0.5, 3)
        if not in_list:
            self.edges.append(Edge(name=edge_name, mean=mean, variance=variance))

    def to_dict(self):
        dict_repr = super().to_dict()
        timepoints = list()
        edges = list()
        for t in self.timepoints:
            timepoints.append(t.to_dict())
        for e in self.edges:
            edges.append(e.to_dict())
        dict_repr.update(timepoints=timepoints)
        dict_repr.update(edges=edges)
        return dict_repr

    @classmethod
    def to_attrs(cls, dict_repr):
        attrs = super().to_attrs(dict_repr)
        timepoints = list()
        edges = list()
        for t in attrs.get("timepoints"):
            timepoints.append(Timepoint.from_dict(t))
        for e in attrs.get("edges"):
            edges.append(Edge.from_dict(e))
        attrs.update(timepoints=timepoints)
        attrs.update(edges=edges)
        return attrs
