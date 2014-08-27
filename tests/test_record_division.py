import unittest

from mdr import Record, RecordFinder

def _create_similarity_cache(elements):

    def _calculate_sim(t1, t2):
        if t1 == t2:
            return 1.0
        elif t1[0] == t2[0]:
            return 0.9
        else:
            return 0

    cache = {}
    for i in range(len(elements)):
        for j in range(len(elements)):
            if j >= i:
                sim = _calculate_sim(elements[i], elements[j])
                cache[(elements[i], elements[j])] = sim
                cache[(elements[j], elements[i])] = sim
    return cache

class RecordFinderTest(unittest.TestCase):

    def test_get_division(self):

        elements = ['a', 'b1', 'c1', 'b2', 'c2']
        clusters = [0, 1, 2, 1, 2]
        cache = _create_similarity_cache(elements)

        rf = RecordFinder(cache)

        records = rf.find_best_division(elements, clusters)

        # records should be: (a), (b1, c1), (b2, c2)
        self.assertEquals(3, len(records))
        self.assertEquals(['a'], [t for t in records[0]])
        self.assertEquals(['b1', 'c1'], [t for t in records[1]])
        self.assertEquals(['b2', 'c2'], [t for t in records[2]])


        elements = ['b1', 'c1', 'b2', 'c2']
        clusters = [1, 2, 1, 2]
        cache = _create_similarity_cache(elements)

        rf = RecordFinder(cache)

        records = rf.find_best_division(elements, clusters)

        # records should be: (b1, c1), (b2, c2)
        self.assertEquals(2, len(records))
        self.assertEquals(['b1', 'c1'], [t for t in records[0]])
        self.assertEquals(['b2', 'c2'], [t for t in records[1]])


        elements = ['b1', 'b2', 'b3', 'b4']
        clusters = [1, 1, 1, 1]
        cache = _create_similarity_cache(elements)

        rf = RecordFinder(cache)

        records = rf.find_best_division(elements, clusters)

        # records should be: (b1, b2, b3, b4))
        self.assertEquals(4, len(records))
        self.assertEquals(['b1'], [t for t in records[0]])
        self.assertEquals(['b2'], [t for t in records[1]])
        self.assertEquals(['b3'], [t for t in records[2]])
        self.assertEquals(['b4'], [t for t in records[3]])


        elements = ['b1', 'b2', 'b3', 'b4']
        clusters = [1, 1, 1, 2]
        cache = _create_similarity_cache(elements)

        rf = RecordFinder(cache)

        records = rf.find_best_division(elements, clusters)

        # records should be: (b1, b2, (b3, b4))
        self.assertEquals(3, len(records))
        self.assertEquals(['b1'], [t for t in records[0]])
        self.assertEquals(['b2'], [t for t in records[1]])
        self.assertEquals(['b3', 'b4'], [t for t in records[2]])


        # no repitions, no data records
        elements = ['a', 'b', 'c', 'd']
        clusters = [1, 2, 3, 4]
        cache = _create_similarity_cache(elements)

        rf = RecordFinder(cache)

        records = rf.find_best_division(elements, clusters)
        self.assertIsNone(records)
