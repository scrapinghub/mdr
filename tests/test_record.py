import unittest
from lxml.html import etree

from mdr import RecordAligner, Record

t1 = etree.XML("""<root>
                    <a></a>
                    <b></b>
                    <c></c>
                  </root>
                """)

t2 = etree.XML("""<root>
                    <a></a>
                    <b></b>
                    <c></c>
                 </root>""")

t3 = etree.XML("""<root>
                    <a></a>
                    <b></b>
                    <c></c>
                  </root>""")

t4 = etree.XML("""<root>
                    <a></a>
                    <b></b>
                    <c></c>
                    <d></d>
                  </root>
            """)

class RecordAlignerTest(unittest.TestCase):

    def test_full_align(self):

        ra = RecordAligner()
        records = [Record(t1), Record(t2), Record(t3)]
        seed, mappings = ra.align(records)

        self.assertEqual(3, len(mappings))

        # all the elements from seed should matched to other 2 trees
        for tag in ['root', 'a', 'b', 'c']:
            e = seed[0].xpath('//%s' % tag)[0]
            expected = []
            for record, mapping in mappings.iteritems():
                expected.append(mapping[e].tag)
            self.assertEqual([tag] * 3, expected)

    def test_align_with_record(self):

        ra = RecordAligner()
        seed_record = Record(t4)

        records = [Record(t1), Record(t2), Record(t3)]
        seed, mappings = ra.align(records, seed_record)

        self.assertEqual(4, len(mappings))

        # all the elements from seed should matched to other 3 trees
        for tag in ['root', 'a', 'b', 'c']:
            root = seed[0].xpath('//%s' % tag)[0]
            expected = []
            for record, mapping in mappings.iteritems():
                if seed_record == record:
                    continue
                expected.append(mapping[root].tag)
            self.assertEqual([tag] * 3, expected)

if __name__ == '__main__':
    unittest.main()
