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
from .tree import PartialTreeAligner, clustered_tree_match
from .utils import split_sequence, common_prefix, simplify_xpath

class Record(object):
    """A class represent a data record.

    Usually it just a list of DOM elements.
    """
    def __init__(self, *trees):
        self.trees = trees

    def __len__(self):
        return len(self.trees)

    def __iter__(self):
        return iter(self.trees)

    def __getitem__(self, item):
        return self.trees[item]

    def __str__(self):
        return '<Record [%s]>' % ", ".join(repr(tree) for tree in self.trees)

    def size(self):
        return sum(tree_size(t) for t in self.trees)

class MDR(object):
    """
    Mining Data Record base on clustering and tree similarity.

    This class follow the approach in [1]_ but change the similarity from
    string edit distance to clustered tree match in [2]_ and [3]_.

    Parameters
    ----------
    threshold: float
        the similarity threshold to cluster the DOM trees.

    References
    ----------
    .. [1] Using clustering and edit distance techniques for automatic web data extraction
    <http://link.springer.com/chapter/10.1007/978-3-540-76993-4_18>

    .. [2] Web Data Extraction Based on Partial Tree Alignment
    <http://doi.acm.org/10.1145/1060745.1060761>

    .. [3] Automatic Wrapper Adaptation by Tree Edit Distance Matching
    <http://arxiv.org/pdf/1103.1252.pdf>
    """
    def __init__(self, threshold=0.9):
        self.threshold = threshold
        self.tree_sim_cache = {}
        self.ra = RecordAligner()

    def list_candidates(self, html, encoding='utf8'):
        """
        list all the data record candidates.

        Returns
        -------
        A sorted list of elements with descreasing order of odds of being an candidate.
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

    def extract(self, element, record=None):
        """
        extract the data record from data record candidate.

        Parameters
        ----------
        element: lxml HTML element
            the HTML element of the candidate

        record: optional
            The seed record learned before.
            used to speed up the extraction without finding the seed elements.

        See Also
        --------
        ``RecordAligner``

        Returns
        -------
        seed_record: ``Record``
             the seed record to match against other record trees.

        mappings: dict
             a dict mapping from aligned record to a nested dict mapping from seed element to element.

        """
        if record:
            n = len(element)
            clusters = []
            # use index as cluster id
            for i in range(n):
                sims = [[clustered_tree_match(element[i], record[j]), j] for j in range(len(record))]
                clusters.append(max(sims, key=operator.itemgetter(0))[1])
            rf = RecordFinder()
            records = rf.find_division(element.getchildren(), clusters, 0)

        else:
            m = self.calculate_similarity_matrix(element)
            clusters = self.hcluster(m)
            assert len(clusters) == len(m)

            rf = RecordFinder(self.tree_sim_cache)
            records = rf.find_best_division(element.getchildren(), clusters)

        if records:
            seed_record, mappings = self.ra.align(records, record)
            if record:
                mappings.pop(record)
            return seed_record, mappings

        return None, {}


    def calculate_similarity_matrix(self, element):
        """calculate the similarity matrix for each child of the given element
        """
        n = len(element)

        m = np.zeros((n, n), np.float)
        for i in range(n):
            for j in range(n):
                if j >= i:
                    m[i, j] = clustered_tree_match(element[i], element[j])
                    self.tree_sim_cache[(element[i], element[j])] = m[i, j]
                    self.tree_sim_cache[(element[j], element[i])] = m[i, j]
                    m[j, i] = m[i, j]
        return m

    def hcluster(self, m):
        """hierarchy clustering base on the given similarity matrix.
        """
        L = sch.linkage(m, method='complete')
        ind = sch.fcluster(L, self.threshold, 'distance')
        return ind.tolist()

class RecordFinder(object):
    """
    A class to find the record from a list of elements.
    """
    def __init__(self, cache={}):
        self.tree_similarity_cache = dict(cache)

    def find_best_division(self, elements, clusters):
        """find the best record division

        Parameters
        ----------
        elements: list
            a list of the HTML element
        clusters: list
            a list of the cluster id for each element in ``elements``

        Returns
        -------
        A list of ``Record``
        """
        assert len(elements) == len(clusters)

        if len(set(clusters)) == len(clusters):
            return None

        all_records = []

        for c in set(clusters):
            records = []
            for group in split_sequence(zip(elements, clusters), lambda x: x[1] == c):
                _clusters = [g[1] for g in group]
                if len(_clusters) < len(clusters):
                    records.append(Record(*[g[0] for g in group]))

            if not records:
                continue

            similarities = [self.calculate_record_similarity(r1, r2) for r1, r2 in itertools.combinations(records, 2)]
            average_sim = sum(similarities) / (len(similarities) + 1)

            all_records.append([average_sim, records])

        return max(all_records, key=operator.itemgetter(0))[1]

    def find_division(self, elements, clusters, cluster):
        """ find the division with given cluster as seperator

        Parameters
        ----------
        elements: list
            a list of the HTML element
        clusters: list
            a list of the cluster id for each element in ``elements``
        cluster: int
            the cluster id to split the elements.

        Returns
        -------
        A list of ``Record``
        """
        assert len(elements) == len(clusters)

        if len(set(clusters)) == len(clusters):
            return None

        records = []

        for group in split_sequence(zip(elements, clusters), lambda x: x[1] == cluster):
            _clusters = [g[1] for g in group]
            if len(_clusters) < len(clusters):
                records.append(Record(*[g[0] for g in group]))

        return records

    def calculate_record_similarity(self, r1, r2):
        """calculate similarity between two Records.
        """

        m = np.zeros((len(r1)+1, len(r2)+1), np.float)

        for i in xrange(1, len(m)):
            for j in xrange(1, len(m[0])):
                sim = self.tree_similarity_cache.get((r1[i - 1], r2[j - 1]))
                assert sim != None, 'tree %s %s not in cache' % (r1[i-1], r2[j-1])
                m[i, j] = max(m[i, j - 1], m[i - 1, j], m[i - 1][j - 1] + sim)

        return m[i, j] / max(m.shape[0], m.shape[1])

class RecordAligner(object):

    def __init__(self):
        self.pta = PartialTreeAligner()

    def align(self, records, record=None):
        """Partial align multiple data records with partial tree match [1]_

        Parameters
        ----------
        records: list
            A list of the data records.

        record: optional
            The seed record learned before.
            used to speed up the extraction without finding the seed elements.

        Returns
        -------
        seed_record: ``Record``
             the seed record to match against other record trees.

        mappings: a dict with record as key and a nested dict map from seed element to aligned element.

        References
        ----------
        .. [1] Web Data Extraction Based on Partial Tree Alignment
        <http://doi.acm.org/10.1145/1060745.1060761>

        """
        if record:
            seed = record
        else:
            # find biggest record
            seed = max(records, key=Record.size)
            records.remove(seed)

        seed_copy = copy.deepcopy(seed)

        mappings = collections.OrderedDict({seed: self._create_mapping(seed_copy, seed)})

        R = []
        while len(records):
            next = records.pop(0)
            modified, partial_match, aligned = self.pta.align_records(seed_copy, next)

            mappings.update({next: aligned})

            if modified:
                records.extend(R)
                R = []
            else:
                # add it back to try it later since seed might change
                if partial_match:
                    R.append(next)

        return seed_copy, mappings

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
