import unittest
from lxml.html import fragment_fromstring
from mdr.mdr import MDR, Record

from . import get_page

def assert_element(expected_tag, expected_class, expected_id, element):
    assert expected_tag == element.tag
    assert expected_class == element.attrib.get('class', '')
    assert expected_id == element.attrib.get('id', '')

class MdrTest(unittest.TestCase):

    def test_detect(self):
        page = get_page('htmlpage0')
        mdr = MDR()
        candidates, doc = mdr.list_candidates(page, 'utf8')

        assert_element('ul', "ylist ylist-bordered reviews", '', candidates[0])

    def test_cluster(self):
        page = get_page('htmlpage0')
        mdr = MDR()
        candidates, doc = mdr.list_candidates(page, 'utf8')
        m = mdr.calculate_similarity_matrix(candidates[0])
        self.assertEquals(1, len(set(mdr.hcluster(m))))

    def test_extract(self):
        fragment = fragment_fromstring(get_page('fragment0'))
        mdr = MDR()
        seed_record, mapping = mdr.extract(fragment)

        # record only have 1 <li> elememt
        self.assertEquals(1, len(seed_record))

        div = seed_record[0].xpath('//div[contains(@class, "review")]')[0]
        # div is the top element of <li>, and there are 40 items in total, so
        # there are 39 mapped to the div in seed.
        self.assertEquals(39, len(mapping[div]))

    def test_extract_with_seed(self):
        fragment = fragment_fromstring(get_page('fragment0'))
        mdr = MDR()
        seed_record = Record(fragment[0])
        seed_record_copy, mapping = mdr.extract(fragment, seed_record)

         # record only have 1 <li> elememt
        self.assertEquals(1, len(seed_record_copy))

        div = seed_record_copy[0].xpath('//div[contains(@class, "review")]')[0]
        # div is the top element of <li>, and there are 40 items in total
        self.assertEquals(40, len(mapping[div]))

if __name__ == '__main__':
    unittest.main()