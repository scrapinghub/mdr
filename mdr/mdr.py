# -*- coding: utf-8 -*-
import copy
import collections
import itertools
import operator

from cStringIO import StringIO
from lxml import etree

import numpy as np
import scipy.cluster.hierarchy as sch

from ._tree import tree_size
from .tree import PartialTreeAligner, clustered_tree_match, normalized_simple_tree_match
from .utils import chop, reverse_dict, common_prefix, simplify_xpath

class Record(object):
    def __init__(self, *trees):
        self.trees = trees

    def __len__(self):
        return len(self.trees)

    def __iter__(self):
        return iter(self.trees)

    def __getitem__(self, item):
        return self.trees[item]

    def __str__(self):
        return 'Record %s [%s..%s]' % (len(self.trees), self.trees[0], self.trees[-1])

    @staticmethod
    def size(record):
        return sum(tree_size(t) for t in record.trees)

class MDR(object):
    """
    Mining Data Record base on clustering and tree similarity.

    Notes
    -----
    This class follow the approach in [1] but change the similarity from
    string edit distance to clustered tree match in [2] and [3].

    References
    ----------
    [1] Using clustering and edit distance techniques for automatic web data extraction
    <http://link.springer.com/chapter/10.1007/978-3-540-76993-4_18>

    [2] Web Data Extraction Based on Partial Tree Alignment
    <http://doi.acm.org/10.1145/1060745.1060761>

    [3] Automatic Wrapper Adaptation by Tree Edit Distance Matching
    <http://arxiv.org/pdf/1103.1252.pdf>
    """
    def __init__(self, threshold=0.9):
        self.threshold = threshold
        self.tree_sim_cache = {}
        self.ra = RecordAligner()

    def list_candidates(self, html, encoding='utf8'):
        """
        list all the data record candidates.

        Notes
        -----
        The idea is the find the elements has the lots of text nodes.

        Returns
        -------
        A sorted list of elements with descreaing order of odds of being an candidate.
        """
        if isinstance(html, unicode):
            html = html.encode(encoding)

        parser = etree.HTMLParser(encoding=encoding)
        doc = etree.parse(StringIO(html), parser)

        d = {}
        # find all the non-empty text nodes
        for e in doc.xpath('//*/text()[normalize-space()]'):
            p = e.getparent()
            xpath = doc.getpath(p)
            d.setdefault(simplify_xpath(xpath), []).append(xpath)

        counter = collections.Counter()
        for key, elements in d.iteritems():
            deepest_common_ancestor = "/".join(common_prefix(*[xpath.split('/') for xpath in elements]))
            counter[deepest_common_ancestor] += 1

        return [doc.xpath(k)[0] for k,v in sorted(counter.items(), key=operator.itemgetter(1), reverse=True)], doc

    def extract(self, element, **kwargs):
        """
        extract the data record from data record candidate.
        """
        m = self.calculate_similarity_matrix(element)
        clusters = self.hcluster(m)
        all_records = []

        # for each cluster type check startswith and ends with
        for c in set(clusters):
            records = []

            for group in chop(clusters, c):
                _clusters = [g[0] for g in group]
                _indexes = [g[1] for g in group]
                if c in _clusters and len(_clusters) < len(clusters):
                    records.append(Record(*[element[i] for i in _indexes]))

            if not records:
                continue

            similarities = [self.calculate_record_similarity(r1, r2) for r1, r2 in itertools.combinations(records, 2)]
            average_sim = sum(similarities) / (len(similarities) + 1)

            all_records.append([average_sim, records])

        records = max(all_records, key=operator.itemgetter(0))[1]
        return self.ra.align(*records, **kwargs)

    def calculate_similarity_matrix(self, doc):
        n = len(doc)
        m = np.zeros((n, n), np.float)
        for i in range(n):
            for j in range(n):
                if j >= i:
                    m[i, j] = clustered_tree_match(doc[i], doc[j])
                    self.tree_sim_cache.setdefault((doc[i], doc[j]), m[i, j])
                    self.tree_sim_cache.setdefault((doc[j], doc[i]), m[i, j])
                    m[j, i] = m[i, j]
        return m

    def hcluster(self, m):
        """
        hierarchy clustering base on the given similarity matrix.
        """
        L = sch.linkage(m, method='complete')
        ind = sch.fcluster(L, self.threshold, 'distance')
        return ind.tolist()

    def calculate_record_similarity(self, r1, r2):
        """
        calculate similarity between two Record.
        """
        m = np.zeros((len(r1)+1, len(r2)+1), np.float)
        for i in xrange(1, len(m)):
            for j in xrange(1, len(m[0])):
                sim = self.tree_sim_cache.get((r1[i - 1], r2[j - 1]))
                assert sim != None, 'tree %s %s not in cache' % (r1[i-1], r2[j-1])
                m[i, j] = max(m[i, j - 1], m[i - 1, j], m[i - 1][j - 1] + sim)

        return m[i, j]

class RecordAligner(object):

    def __init__(self):
        self.pta = PartialTreeAligner()

    def align(self, *records, **kwargs):
        """partial align multiple data records.

        for example:

        >>> from lxml.html import fragment_fromstring
        >>> t1 = fragment_fromstring("<p> <x1></x1> <x2></x2> <x3></x3> <x></x> <b></b> <d></d> </p>")
        >>> t2 = fragment_fromstring("<p> <b></b> <n></n> <c></c> <k></k> <g></g> </p>")
        >>> t3 = fragment_fromstring("<p> <b></b> <c></c> <d></d> <h></h> <k></k> </p>")

        >>> ra = RecordAligner()
        >>> _, _, seed = ra.align(Record(t1), Record(t2), Record(t3))
        >>> [e.tag for e in seed[0]]       # seed is a new record with fully aligned with other tress
        ['x1', 'x2', 'x3', 'x', 'b', 'n', 'c', 'd', 'h', 'k', 'g']
        >>> [e.tag for e in t1]         # the old DOM tree stay same
        ['x1', 'x2', 'x3', 'x', 'b', 'd']
        """
        cmp = kwargs.pop('cmp', None) or Record.size
        sorted_records = sorted(records, key=cmp)

        # find largest record
        seed = kwargs.pop('seed_record', None) or sorted_records.pop()

        seed_copy = copy.deepcopy(seed)

        # a dict like {t2: {}, t3: {}, ...}
        # the nested dictionary is mapping from seed tree elements to target elements
        mappings = collections.defaultdict(dict)

        # a dict mapping from tree elements to seed elements
        reverse_mappings = {}

        initial_mapping = self._create_mapping(seed_copy, seed)
        reverse_mappings.update(reverse_dict(initial_mapping))

        mappings.setdefault(seed, initial_mapping)

        R = []
        while len(sorted_records):
            next = sorted_records.pop()
            modified, partial_match, aligned = self.pta.align_records(seed_copy, next)
            reverse_mappings.update(reverse_dict(aligned))

            mappings.update({next: aligned})

            if modified:
                sorted_records.extend(R)
                R = []
            else:
                # add it back to try it later since seed might change
                if partial_match:
                    R.append(next)

        return mappings, reverse_mappings, seed_copy

    def _create_mapping(self, seed, tree):
        """create a mapping from seed tree to another tree.

        for example:

        >>> from lxml.html import fragment_fromstring
        >>> t1 = fragment_fromstring("<p> <a></a> <b></b> </p>")
        >>> t2 = fragment_fromstring("<p> <a></a> <b></b> </p>")
        >>> ra = RecordAligner()
        >>> d = ra._create_mapping(Record(t1), Record(t2))
        >>> d[t1] == t2
        True
        """
        d = {}
        for s, e in zip(seed, tree):
            d[s] = e
            d.update(self._create_mapping(s, e))
        return d
