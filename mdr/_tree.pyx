cimport cython
import numpy as np
cimport numpy as np

def tree_size(t):
    if len(t) == 0:
        return 1
    return sum(tree_size(child) for child in t) + 1

@cython.boundscheck(False)
@cython.wraparound(False)
def simple_tree_match(t1, t2):

    if t1 is None or t2 is None:
        return 0

    if t1.tag != t2.tag:
        return 0

    m = np.zeros((len(t1) + 1, len(t2) + 1), np.int)

    for i from 1 <= i < m.shape[0]:
        for j from 1 <= j < m.shape[1]:
            m[i, j] = max(m[i, j - 1], m[i - 1, j], m[i - 1, j - 1] + simple_tree_match(t1[i - 1], t2[j - 1]))
    return 1 + m[m.shape[0]-1, m.shape[1]-1]

@cython.boundscheck(False)
@cython.wraparound(False)
def clustered_tree_match(t1, t2):

    if t1 is None or t2 is None:
        return 0

    if t1.tag != t2.tag:
        return 0

    m = np.zeros((len(t1) + 1, len(t2) + 1), np.int)

    for i from 1 <= i < m.shape[0]:
        for j from 1 <= j < m.shape[1]:
            m[i][j] = max(m[i, j - 1], m[i - 1, j], m[i - 1, j - 1] + clustered_tree_match(t1[i - 1], t2[j - 1]))

    if len(t1) and len(t2):
        return m[m.shape[0]-1][m.shape[1]-1] * 1.0 / max(m.shape)
    else:
        return m[m.shape[0]-1][m.shape[1]-1] + 1.0 / max(m.shape)