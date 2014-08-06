# -*- coding: utf-8 -*-
import re
import itertools

def find_continous_subsequence(iterable, predicate):
    """
    find the continuous subsequence with predicate function return true

    >>> find_continous_subsequence([2, 1, 2, 4], lambda x: x % 2 == 0)
    [[2], [2, 4]]

    >>> find_continous_subsequence([2, 1, 2, 4], lambda x: x % 2 != 0)
    [[1]]
    """
    seqs = []
    for key, values in itertools.groupby(iterable, key=predicate):
        if key == True:
            seqs.append(list(values))
    return seqs

def split_sequence(seq, predicate):
    """
    split the sequence at the position when predicate return true

    >>> list(split_sequence([0, 1, 2, 1, 2], lambda x: x == 1))
    [[0], [1, 2], [1, 2]]

    >>> list(split_sequence([0, 1, 2, 1, 2, 1], lambda x: x == 2))
    [[0, 1], [2, 1], [2, 1]]

    >>> list(split_sequence([('a', 1), ('b', 2), ('c', 1)], lambda x: x[1] == 1))
    [[('a', 1), ('b', 2)], [('c', 1)]]
    """
    seqs = []
    for s in seq:
        if predicate(s):
            if seqs:
                yield seqs
            seqs = [s]
        else:
            seqs.append(s)
    if seqs:
        yield seqs

def reverse_dict(d):
    return dict(reversed(item) for item in d.items())

def common_prefix(*sequences):
    """determine the common prefix of all sequences passed

    For example:
    >>> common_prefix('abcdef', 'abc', 'abac')
    ['a', 'b']
    """
    prefix = []
    for sample in itertools.izip(*sequences):
        first = sample[0]
        if all([x == first for x in sample[1:]]):
            prefix.append(first)
        else:
            break
    return prefix

def simplify_xpath(xpath):
    return re.sub('\[\d+\]', '', xpath)
