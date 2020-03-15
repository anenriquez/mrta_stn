import numpy as np
from stn.utils.as_dict import AsDictMixin


class InterTimepointConstraint(AsDictMixin):
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


class TimepointConstraint(AsDictMixin):
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
    def __init__(self, task_id, timepoint_constraints, inter_timepoint_constraints):

        """ Constructor for the Task object

        Args:
            task_id (UUID): An instance of an UUID object
            timepoint_constraints (list): list of timepoint constraints (TimepointConstraint)
            inter_timepoint_constraints (list): list of inter timepoint constraints (InterTimepointConstraint)
            hard_constraints (bool): False if the task can be
                                    scheduled ASAP, True if the task is not flexible. Defaults to True
        """
        self.task_id = task_id
        self.timepoint_constraints = list()
        self.inter_timepoint_constraints = list()

        for constraint in timepoint_constraints:
            self.timepoint_constraints.append(constraint)
        for constraint in inter_timepoint_constraints:
            self.inter_timepoint_constraints.append(constraint)

    def __str__(self):
        to_print = ""
        to_print += "{} \n".format(self.task_id)
        to_print += "TimepointConstraints: \n"
        for constraint in self.timepoint_constraints:
            to_print += str(constraint) + "\t"
        to_print += "\n InterTimepointConstraints\n"
        for constraint in self.inter_timepoint_constraints:
            to_print += str(constraint) + "\t"
        return to_print

    def get_timepoint_constraint(self, constraint_name):
        return [constraint for constraint in self.timepoint_constraints
                if constraint.name == constraint_name].pop()

    def get_inter_timepoint_constraint(self, constraint_name):
        return [constraint for constraint in self.inter_timepoint_constraints
                if constraint.name == constraint_name].pop()

    def update_timepoint_constraint(self, constraint_name, r_earliest_time, r_latest_time=np.inf):
        in_list = False
        for constraint in self.timepoint_constraints:
            if constraint.name == constraint_name:
                in_list = True
                constraint.r_earliest_time = r_earliest_time
                constraint.r_latest_time = r_latest_time
        if not in_list:
            self.timepoint_constraints.append(TimepointConstraint(constraint_name,
                                                                  r_earliest_time,
                                                                  r_latest_time))

    def update_inter_timepoint_constraint(self, name, mean, variance):
        in_list = False
        for constraint in self.inter_timepoint_constraints:
            if constraint.name == name:
                in_list = True
                constraint.mean = round(mean, 3)
                constraint.variance = round(variance, 3)
                constraint.standard_dev = round(variance ** 0.5, 3)
        if not in_list:
            self.inter_timepoint_constraints.append(InterTimepointConstraint(name=name, mean=mean,
                                                                             variance=variance))

    def to_dict(self):
        dict_repr = super().to_dict()
        timepoint_constraints = list()
        inter_timepoint_constraints = list()
        for c in self.timepoint_constraints:
            timepoint_constraints.append(c.to_dict())
        for c in self.inter_timepoint_constraints:
            inter_timepoint_constraints.append(c.to_dict())
        dict_repr.update(timepoint_constraints=timepoint_constraints)
        dict_repr.update(inter_timepoint_constraints=inter_timepoint_constraints)
        return dict_repr

    @classmethod
    def to_attrs(cls, dict_repr):
        attrs = super().to_attrs(dict_repr)
        timepoint_constraints = list()
        inter_timepoint_constraints = list()
        for c in attrs.get("timepoint_constraints"):
            timepoint_constraints.append(TimepointConstraint.from_dict(c))
        for c in attrs.get("inter_timepoint_constraints"):
            inter_timepoint_constraints.append(InterTimepointConstraint.from_dict(c))
        attrs.update(timepoint_constraints=timepoint_constraints)
        attrs.update(inter_timepoint_constraints=inter_timepoint_constraints)
        return attrs
