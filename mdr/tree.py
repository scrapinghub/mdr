# -*- coding: utf-8 -*-
import numpy as np
import copy

from .utils import find_continous_subsequence, reverse_dict
from ._tree import _clustered_tree_match, _simple_tree_match, tree_size

def normalized_simple_tree_match(t1, t2):
    t1size = tree_size(t1)
    t2size = tree_size(t2)
    return _simple_tree_match(t1, t2) / (2.0 * (t1size + t2size))

def clustered_tree_match(t1, t2, c1=1, c2=1):
    return _clustered_tree_match(t1, t2, c1, c2)

class TreeAlignment(object):

    TRACE_LEFT = 1
    TRACE_UP = 2
    TRACE_DIAG = 3

    def __init__(self, first=None, second=None, score=0):
        self.first = first
        self.second = second
        self.score = score
        self.subs = []

    def add(self, alignment):
        if self.first is None and self.second is None:
            self.first, self.second = alignment.first, alignment.second
        else:
            self.subs.append(alignment)
        self.subs.extend(alignment.subs)

    @property
    def tag(self):
        assert self.first.tag == self.second.tag
        return self.first.tag

    def __str__(self):
        return '{} {}: {}'.format(self.first, self.subs, self.score)

class SimpleTreeAligner(object):

    def align_records(self, r1, r2):
        """
        Align two records.
        """
        alignment = TreeAlignment()

        m = np.zeros((len(r1)+1, len(r2)+1), np.int)
        align_matrix = np.array([[0 for _ in range(len(r2))] for _ in range(len(r1))], np.object)
        trace = np.zeros((len(r1), len(r2)), np.int)

        for i in xrange(1, m.shape[0]):
            for j in xrange(1, m.shape[1]):
                if m[i, j-1] > m[i-1, j]:
                    m[i, j] = m[i, j-1]
                    trace[i-1, j-1] = TreeAlignment.TRACE_LEFT
                else:
                    m[i, j] = m[i-1, j]
                    trace[i-1, j-1] = TreeAlignment.TRACE_UP

                align_matrix[i-1, j-1] = self.align_tree(r1[i - 1], r2[j - 1])
                score = m[i-1, j-1] + align_matrix[i-1, j-1].score

                if score > m[i][j]:
                    m[i, j] = score
                    trace[i-1, j-1] = TreeAlignment.TRACE_DIAG

        row = trace.shape[0] - 1
        col = trace.shape[1] - 1

        while row >= 0 and col >= 0:
            if trace[row][col] == TreeAlignment.TRACE_DIAG:
                alignment.add(align_matrix[row][col])
                row -= 1
                col -= 1
            elif trace[row][col] == TreeAlignment.TRACE_UP:
                row -= 1
            elif trace[row][col] == TreeAlignment.TRACE_LEFT:
                col -= 1

        alignment.score = m[m.shape[0]-1][m.shape[1] - 1]
        return alignment

    def align_tree(self, t1, t2):
        """
        align two DOM trees.
        """
        if t1 is None or t2 is None:
            return TreeAlignment()

        if t1.tag != t2.tag:
            return TreeAlignment()

        alignment = TreeAlignment(t1, t2)

        m = np.zeros((len(t1)+1, len(t2)+1), np.int)
        align_matrix = np.array([[0 for _ in range(len(t2))] for _ in range(len(t1))], np.object)
        trace = np.zeros((len(t1), len(t2)), np.int)

        for i in xrange(1, m.shape[0]):
            for j in xrange(1, m.shape[1]):
                if m[i, j - 1] > m[i - 1, j]:
                    m[i, j] = m[i, j - 1]
                    trace[i - 1, j - 1] = TreeAlignment.TRACE_LEFT
                else:
                    m[i, j] = m[i - 1, j]
                    trace[i - 1, j - 1] = TreeAlignment.TRACE_UP
                align_matrix[i - 1, j - 1] = self.align_tree(t1[i - 1], t2[j - 1])
                score = m[i - 1, j - 1] + align_matrix[i - 1, j - 1].score
                if score > m[i, j]:
                    m[i, j] = score
                    trace[i - 1, j - 1] = TreeAlignment.TRACE_DIAG

        row = len(trace) - 1

        if row >= 0:
            col = len(trace[0]) - 1
        else:
            col = -1

        while row >= 0 and col >= 0:
            if trace[row, col] == TreeAlignment.TRACE_DIAG:
                alignment.add(align_matrix[row, col])
                row -= 1
                col -= 1
            elif trace[row, col] == TreeAlignment.TRACE_UP:
                row -= 1
            elif trace[row, col] == TreeAlignment.TRACE_LEFT:
                col -= 1

        alignment.score = 1 + m[len(m) - 1, len(m[0]) - 1]

        if t1.attrib.get('class') and t1.attrib.get('class') == t2.attrib.get('class'):
            alignment.score += 1

        if t1.attrib.get('itemprop') and t1.attrib.get('itemprop') == t2.attrib.get('itemprop'):
            alignment.score += 1

        return alignment

class PartialTreeAligner(object):

    def __init__(self):
        self.sta = SimpleTreeAligner()

    def align_records(self, r1, r2):
        """
        partial align DOM tree list to another DOM tree list.

        e.g. (taken from [1]):

        >>> from lxml.html import fragment_fromstring
        >>> from .mdr import Record
        >>> pta = PartialTreeAligner()

        1. "flanked by 2 sibling nodes"
        >>> t1 = fragment_fromstring("<p> <a></a> <b></b> <e></e> </p>")
        >>> t2 = fragment_fromstring("<p> <b></b> <c></c> <d></d> <e></e> </p>")
        >>> _, _, mapping = pta.align_records(Record(t1), Record(t2))
        >>> [e.tag for e in t1]
        ['a', 'b', 'c', 'd', 'e']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['b', 'c', 'd', 'e', 'p']

        2. "rightmost nodes"
        >>> t1 = fragment_fromstring("<p> <a></a> <b></b> <e></e> </p>")
        >>> t2 = fragment_fromstring("<p> <e></e> <f></f> <g></g> </p>")
        >>> _, _, mapping = pta.align_records(Record(t1), Record(t2))
        >>> [e.tag for e in t1]
        ['a', 'b', 'e', 'f', 'g']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['e', 'f', 'g', 'p']

        3. "leftmost nodes"
        >>> t1 = fragment_fromstring("<p> <a></a> <b></b> <e></e> </p>")
        >>> t2 = fragment_fromstring("<p> <f></f> <g></g> <a></a> </p>")
        >>> _, _, mapping = pta.align_records(Record(t1), Record(t2))
        >>> [e.tag for e in t1]
        ['f', 'g', 'a', 'b', 'e']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['a', 'f', 'g', 'p']

        4. "no unique insertion"
        >>> t1 = fragment_fromstring("<p> <a></a> <b></b> <e></e> </p>")
        >>> t2 = fragment_fromstring("<p> <a></a> <g></g> <e></e> </p>")
        >>> _, _, mapping = pta.align_records(Record(t1), Record(t2))
        >>> [e.tag for e in t1]
        ['a', 'b', 'e']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['a', 'e', 'p']

        5. "multiple unaligned nodes"
        >>> t1 = fragment_fromstring("<p> <x></x> <b></b> <d></d> </p>")
        >>> t2 = fragment_fromstring("<p> <b></b> <c></c> <d></d> <h></h> <k></k> </p>")
        >>> _, _, mapping = pta.align_records(Record(t1), Record(t2))
        >>> [e.tag for e in t1]
        ['x', 'b', 'c', 'd', 'h', 'k']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['b', 'c', 'd', 'h', 'k', 'p']

        References
        ----------
        [1] Web Data Extraction Based on Partial Tree Alignment
        <http://dl.acm.org/citation.cfm?id=1060761>

        """
        alignment = self.sta.align_records(r1, r2)
        aligned = {alignment.first: alignment.second}

        for sub in alignment.subs:
            aligned[sub.first] = sub.second

        # add reverse mapping too
        reverse_aligned = reverse_dict(aligned)

        modified = False

        unaligned_elements = self.find_unaligned_elements(aligned, r2)
        for l in unaligned_elements:
            left_most = l[0]
            right_most = l[-1]

            prev_sibling = left_most.getprevious()
            next_sibling = right_most.getnext()

            if prev_sibling is None:
                if next_sibling is not None:
                    # leftmost alignment
                    next_sibling_match = reverse_aligned.get(next_sibling, None)
                    for i, element in enumerate(l):
                        element_copy = copy.deepcopy(element)
                        next_sibling_match.getparent().insert(i, element_copy)
                        aligned.update({element_copy: element})
                    modified = True
            elif next_sibling is None:
                # rightmost alignment
                prev_sibling_match = reverse_aligned.get(prev_sibling, None)
                previous_match_index = self._get_index(prev_sibling_match)
                # unique insertion
                for i, element in enumerate(l):
                    element_copy = copy.deepcopy(element)
                    prev_sibling_match.getparent().insert(previous_match_index + 1 + i, element_copy)
                    aligned.update({element_copy: element})
                modified = True
            else:
                # flanked by two sibling elements
                prev_sibling_match = reverse_aligned.get(prev_sibling, None)
                next_sibling_match = reverse_aligned.get(next_sibling, None)

                if prev_sibling_match is not None and next_sibling_match is not None:
                    next_match_index = self._get_index(next_sibling_match)
                    previous_match_index = self._get_index(prev_sibling_match)
                    if next_match_index - previous_match_index == 1:
                        # unique insertion
                        for i, element in enumerate(l):
                            element_copy = copy.deepcopy(element)
                            prev_sibling_match.getparent().insert(previous_match_index + 1 + i, element_copy)
                            aligned.update({element_copy: element})
                        modified = True
        return modified, len(unaligned_elements) > 0, aligned

    def find_unaligned_elements(self, aligned, elements):
        """
        find the unaligned elements recursively from elements.

        >>> from lxml.html import fragment_fromstring
        >>> t1 = fragment_fromstring("<div> <h1></h1> <h2></h2> <h5></h5> </div>")
        >>> t2 = fragment_fromstring("<div> <h2></h2> <h3></h3> <h4></h4> <h5></h5> <h6></h6></div>")

        >>> sta = SimpleTreeAligner()
        >>> pta = PartialTreeAligner()
        >>> aligned = dict((align.first, align.second) for align in sta.align_tree(t1, t2).subs)
        >>> unaligned = pta.find_unaligned_elements(aligned, [t2])
        >>> [[e.tag for e in l] for l in unaligned]
        [['h3', 'h4'], ['h6']]
        """
        predicate = lambda x: x not in set(aligned.values())
        unaligned = []

        for element in elements:
            current_level = find_continous_subsequence(element, predicate)
            unaligned.extend(current_level)

            for child in element:
                unaligned.extend(find_continous_subsequence(child, predicate))

        return unaligned

    def _get_index(self, element):
        """
        get the position of the element within the parent.
        """
        return element.getparent().index(element)
