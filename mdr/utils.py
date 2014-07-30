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
    seq = []
    continuous = False

    for i in iterable:
        if predicate(i):
            if continuous:
                seq.append(i)
            else:
                seq = [i]
                continuous = True
        elif continuous:
            seqs.append(seq)
            seq = []
            continuous = False
    if len(seq):
        seqs.append(seq)
    return seqs

def chop(iterable, c):
    """
    chop the iterable by the element equals to c

    >>> list(chop([0, 1, 2, 1, 2], 1))
    [[(0, 0)], [(1, 1), (2, 2)], [(1, 3), (2, 4)]]

    >>> list(chop([0, 1, 2, 1, 2, 1], 2))
    [[(0, 0), (1, 1)], [(2, 2), (1, 3)], [(2, 4), (1, 5)]]
    """
    seqs = []
    for i, s in enumerate(iterable):
        if s == c:
            yield seqs
            seqs = [(s, i)]
        else:
            seqs.append((s, i))
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