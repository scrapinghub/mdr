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
        seed, mapping = ra.align(records)

        self.assertEqual(3, len(seed[0]))

        # all the elements from seed should matched to other 2 trees
        for tag in ['root', 'a', 'b', 'c']:
            e = seed[0].xpath('//%s' % tag)[0]
            self.assertEqual([tag] * 2, [e.tag for e in mapping[e]])

    def test_align_with_record(self):

        ra = RecordAligner()
        record = Record(t4)

        records = [Record(t1), Record(t2), Record(t3)]
        seed, mapping = ra.align(records, record)

        self.assertEqual(4, len(seed[0]))

        # all the elements from seed should matched to other 3 trees
        for tag in ['root', 'a', 'b', 'c']:
            root = seed[0].xpath('//%s' % tag)[0]
            self.assertEqual([tag] * 3, [e.tag for e in mapping[root]])

        # only <d></d> left
        e = seed[0].xpath('//d')[0]
        self.assertEqual(0, len(mapping[e]))

if __name__ == '__main__':
    unittest.main()
