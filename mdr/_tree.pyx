cimport cython
import numpy as np
cimport numpy as np

def tree_size(t):
    if len(t) == 0:
        return 1
    return sum(tree_size(child) for child in t) + 1

@cython.boundscheck(False)
@cython.wraparound(False)
def _simple_tree_match(t1, t2):

    if t1 is None or t2 is None:
        return 0

    if t1.tag != t2.tag:
        return 0

    m = np.zeros((len(t1) + 1, len(t2) + 1), np.int)

    for i from 1 <= i < m.shape[0]:
        for j from 1 <= j < m.shape[1]:
            m[i, j] = max(m[i, j - 1], m[i - 1, j], m[i - 1, j - 1] + _simple_tree_match(t1[i - 1], t2[j - 1]))
    return 1 + m[m.shape[0]-1, m.shape[1]-1]

@cython.boundscheck(False)
@cython.wraparound(False)
def _clustered_tree_match(t1, t2, c1, c2):

    if t1 is None or t2 is None:
        return 0.0

    if t1.tag != t2.tag:
        return 0.0

    m = len(t1)
    n = len(t2)

    matrix = np.zeros((m+1, n+1), np.float)

    for i from 1 <= i < matrix.shape[0]:
        for j from 1 <= j < matrix.shape[1]:
            matrix[i, j] = max(matrix[i, j - 1], matrix[i - 1, j],
                matrix[i - 1, j - 1] + _clustered_tree_match(t1[i - 1], t2[j - 1], m, n))

    # XXX: m and n?
    if m or n:
        return matrix[m, n] / (1.0 * max(c1, c2))
    else:
        return matrix[m, n] + (1.0 / max(c1, c2))
