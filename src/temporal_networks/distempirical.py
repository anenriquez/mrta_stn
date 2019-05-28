# Taken from https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/distempirical.py
#
# MIT License
#
# Copyright (c) 2019 HEATlab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import random
import numpy as np
from scipy.stats import norm

# These variables should never be imported from this file.
_samples = {}
"""Stores a dictionary of the form {key: list of distribution samples}"""
_invcdfs = {}
"""Stores a dictionary of the form {key: list of inverse cdf points}"""

MAX_RESAMPLE = 10


def collect_data(rundir):
    """Unimplemented function intended for empirical data collection"""
    pass


def empirical_sample(distribution_name: str, state=None) -> float:
    """Gets a sample from a specified distribution.

    Return:
        Returns a float from the distribution.
    """
    if state is None:
        return np.random.choice(_samples[distribution_name])
    else:
        return state.choice(_samples[distribution_name])


def norm_sample(mu: float, sigma: float, state=None, res=1000,
                neg=False) -> float:
    """Retrieve a sample from a normal distribution

    Args:
        mu: mean of the normal distribution
        sigma: standard deviation of the normal distribution

    Keyword Args:
        mu: Mean of the normal curve
        sigma (float): Standard Dev of the normal curve
        state (RandomState, optional): Numpy RandomState object to use for the
            sampling. Default is set to None, meaning that we're using the
            global state.
        res (int, optional): Resolution
        neg (bool, optional): If we want to use negative values, set this to
            True. Default is False.
    Return:
        Returns a random sample (float).
    """
    if state is None:
        ans = -1.0
        count = 0
        while ans < 0.0:
            if count > MAX_RESAMPLE:
                ans = 0.0
                break
            ans = np.random.normal(loc=mu, scale=sigma)
            count += 1
    else:
        ans = -1.0
        count = 0
        while ans < 0.0:
            if count > MAX_RESAMPLE:
                ans = 0.0
                break
            ans = state.normal(loc=mu, scale=sigma)
            count += 1
    return ans


def norm_curve(mu: float, sigma: float, res=1000, neg=False):
    """Produces a descritised normal curve.

    Note:
        This function is memoised. We don't want to redo work that we've
        already done.

    Example:
        norm_curve(1.0, 0.0)
    """
    global _samples

    # Memoisation check
    if (mu, sigma, res, neg) in _samples:
        return _samples[(mu, sigma, res, neg)]
    if neg:
        x = np.linspace(norm.ppf(0.003, loc=mu, scale=sigma),
                        norm.ppf(0.997, loc=mu, scale=sigma),
                        res)
    else:
        x = np.linspace(max(norm.ppf(0.003, loc=mu, scale=sigma), 0.0),
                        max(norm.ppf(0.997, loc=mu, scale=sigma), 0.0),
                        res)
    y = norm.pdf(x, loc=mu, scale=sigma)
    # Memoisation
    _samples[(mu, sigma, res, neg)] = (x, y)
    return (x, y)


def invcdf_norm_curve(mu: float, sigma: float, res=1000, neg=False):
    """Generate an inverse CDF curve for a normal distribution
    """
    global _invcdfs
    if (mu, sigma, res, neg) in _invcdfs:
        return _invcdfs[(mu, sigma, res, neg)]
    normx, normy = norm_curve(mu, sigma, res=res, neg=neg)
    delx = normx[1] - normx[0]
    sol = (np.cumsum(normy) * delx, normx)
    _invcdfs[(mu, sigma, res, neg)] = sol
    return sol


def binary_search_lookup(val, l):
    """Returns the index of where the val is in a sorted list.

    If val is not in l, then return the index of the element directly below l.

    Example:
        >>> binary_search_lookup(10.0, [-5.0, 6.0, 10.0, 100.0])
        2
        >>> binary_search_lookup(5.0, [-5.0, 4.0, 10.0, 100.0])
        1
        >>> binary_search_lookup(11.0, [-5.0, 4.0, 10.0, 100.0])
        2
    """
    up = len(l) - 1
    lo = 0
    look = (up + lo) // 2
    while abs(up - lo) > 1:
        if l[look] == val:
            return look
        if val < l[look]:
            # We need to look lower.
            up = look
            look = (up + lo) // 2
        else:
            # We need to look higher.
            lo = look
            look = (up + lo) // 2
    # Didn't find the exact match, return the lower bound then.
    return lo


def invcdf_norm(val: float, mu: float, sigma: float, res=1000, neg=False):
    """Returns the inverse cumulative density function for a normal curve

    Args:
        val (float): input (x-axis) for the inverse CDF.
        mu (float): mean of the normal curve.
        simga (float): sd of the normal curve.
        res (int, optional): resolution of the normal curve.
        neg (bool, optional): Should include negative values in the cdf.
    """
    curve = invcdf_norm_curve(mu, sigma, res=res, neg=neg)
    ans = curve[1][binary_search_lookup(val, curve[0])]
    return ans


def uniform_sample(lb: float, ub: float, random_state=None) -> float:
    """Returns a randomly selected uniform sample

    Args:
        lb: Lower bound of the uniform sample
        ub: Upper bound of the uniform sample
        random_state (optional): Numpy random state to use (default None)

    Return:
        A new sample drawn from the uniform distribution
    """
    if random_state is None:
        return np.random.uniform(lb, ub)
    else:
        return random_state.uniform(lb, ub)


def invcdf_uniform(val: float, lb: float, ub: float) -> float:
    """Returns the inverse CDF lookup of a uniform distribution. Is constant
        time to call.

    Args:
        val: Value between 0 and 1 to calculate the inverse cdf of.
        lb: lower bound of the uniform distribution
        ub: upper bound of the uniform distribution

    Returns:
        Inverse CDF of a uniform distribution for the provided value.

    Examples:
        >>> invcdf_uniform(1, 5, 10)
        10
        >>> invcdf_uniform(0, 5, 10)
        5
        >>> invcdf_uniform(0.5, 5, 10)
        7.5
    """
    if val < 0:
        return -float("inf")
    elif val > 1:
        return float("inf")
    else:
        return val * (ub - lb) + lb


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    import matplotlib.pyplot as plt
    curve = invcdf_norm_curve(5, 1)
    plt.plot(curve[0], curve[1])
    plt.show()
