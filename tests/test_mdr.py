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
        mdr = MDR()

        page = get_page('htmlpage0')
        candidates, doc = mdr.list_candidates(page, 'utf8')
        assert_element('ul', "ylist ylist-bordered reviews", '', candidates[0])

        page1 = get_page('htmlpage1')
        candidates, doc = mdr.list_candidates(page1, 'utf8')
        assert_element('div', "tab-pane fade in active", 'reviews', candidates[0])

    def test_cluster(self):
        mdr = MDR()

        page = get_page('htmlpage0')
        candidates, doc = mdr.list_candidates(page, 'utf8')
        m = mdr.calculate_similarity_matrix(candidates[0])
        self.assertEquals(1, len(set(mdr.hcluster(m))))

        page1 = get_page('htmlpage1')
        candidates, doc = mdr.list_candidates(page1, 'utf8')
        m = mdr.calculate_similarity_matrix(candidates[0])
        # first element is different from the rests
        self.assertEquals(3, len(set(mdr.hcluster(m))))


    def test_extract(self):
        mdr = MDR()

        page = get_page('htmlpage0')
        candidates, doc = mdr.list_candidates(page, 'utf8')
        seed_record, mapping = mdr.extract(candidates[0])

        # record only have 1 <li> elememt
        self.assertEquals(1, len(seed_record))

        # div is the top element of <li>, and there are 40 items in total, so
        # there are 39 mapped to the div in seed.
        self.assertEquals(39, len(mapping[seed_record[0]]))

        page1 = get_page('htmlpage1')
        candidates, doc = mdr.list_candidates(page1, 'utf8')
        seed_record, mapping = mdr.extract(candidates[0])

        # record have 2 elememts: <div class='divider-horizontal'> and <div class='hreview'>
        self.assertEquals(2, len(seed_record))
        self.assertEquals('divider-horizontal', seed_record[0].attrib.get('class'))
        self.assertEquals('hreview', seed_record[1].attrib.get('class'))

        self.assertEquals(28, len(mapping[seed_record[0]]))
        self.assertEquals(28, len(mapping[seed_record[1]]))

    def test_extract_with_seed(self):
        mdr = MDR()

        page = get_page('htmlpage0')
        candidates, doc = mdr.list_candidates(page, 'utf8')
        # we known first element can be used as seed
        seed_record = Record(candidates[0][0])

        fragment = fragment_fromstring(get_page('fragment0'))
        seed_record_copy, mapping = mdr.extract(fragment, seed_record)

         # record only have 1 <li> elememt
        self.assertEquals(1, len(seed_record_copy))
        div = seed_record_copy[0]
        # div is the top element of <li>, and there are 40 items in total
        self.assertEquals(40, len(mapping[div]))

    def test_extract_with_seed2(self):

        mdr = MDR()
        page1 = get_page('htmlpage1')
        candidates, doc = mdr.list_candidates(page1, 'utf8')
        seed_record = Record(candidates[0][1], candidates[0][2])

        fragment1 = fragment_fromstring(get_page('fragment1'))
        seed_record_copy, mapping = mdr.extract(fragment1, seed_record)

        self.assertEquals(2, len(seed_record_copy))
        self.assertEquals('hreview', seed_record_copy[1].attrib.get('class'))
        self.assertEquals(27, len(mapping[seed_record_copy[1]]))

if __name__ == '__main__':
    unittest.main()
