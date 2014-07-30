import unittest

from ..mdr import MDR
from ..tests import get_page

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

if __name__ == '__main__':
    unittest.main()