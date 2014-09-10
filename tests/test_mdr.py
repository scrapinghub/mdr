import unittest
from lxml.html import fragment_fromstring
from mdr import MDR, Record

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
        seed_record, mappings = mdr.extract(candidates[0])

        # record only have 1 <li> elememt
        self.assertEquals(1, len(seed_record))

        # div is the top element of <li>, and there are 40 items in total
        self.assertEquals(40, len(mappings))

        page1 = get_page('htmlpage1')
        candidates, doc = mdr.list_candidates(page1, 'utf8')
        seed_record, mappings = mdr.extract(candidates[0])

        # record have 2 elememts: <div class='divider-horizontal'> and <div class='hreview'>
        self.assertEquals(2, len(seed_record))
        self.assertEquals('divider-horizontal', seed_record[0].attrib.get('class'))
        self.assertEquals('hreview', seed_record[1].attrib.get('class'))

        self.assertEquals(30, len(mappings))

        fragment2 = fragment_fromstring(get_page('fragment2'))
        seed_record, mappings = mdr.extract(fragment2)

        # record have 2 elememts: <div class='row'> and <div class='row'>
        self.assertEquals(2, len(seed_record))
        self.assertEquals('row', seed_record[0].attrib.get('class'))
        self.assertEquals(7, len(mappings))


    def test_extract_with_seed(self):
        mdr = MDR()

        page = get_page('htmlpage0')
        candidates, doc = mdr.list_candidates(page, 'utf8')
        # we known first element can be used as seed
        seed_record = Record(candidates[0][0])

        fragment = fragment_fromstring(get_page('fragment0'))
        seed_record_copy, mappings = mdr.extract(fragment, seed_record)

        # record only have 1 <li> elememt
        self.assertEquals(1, len(seed_record_copy))
        # 40 items (records)
        self.assertEquals(40, len(mappings))

        extracted_dates = []

        for record, mapping in mappings.iteritems():
            for k, v in mapping.iteritems():
                if k.attrib.get('itemprop') == 'datePublished':
                    extracted_dates.append(v.attrib.get('content'))

        self.assertEquals(extracted_dates[0], '2014-07-02')
        self.assertEquals(extracted_dates[-1], '2014-05-18')

    def test_extract_with_seed2(self):

        mdr = MDR()
        page1 = get_page('htmlpage1')
        candidates, doc = mdr.list_candidates(page1, 'utf8')
        seed_record = Record(candidates[0][1], candidates[0][2])

        fragment1 = fragment_fromstring(get_page('fragment1'))
        seed_record_copy, mappings = mdr.extract(fragment1, seed_record)

        self.assertEquals(2, len(seed_record_copy))
        self.assertEquals('hreview', seed_record_copy[1].attrib.get('class'))
        # 27 items (records)
        self.assertEquals(27, len(mappings))

        extracted_dates = []
        extracted_texts = []

        for record, mapping in mappings.iteritems():
            for k, v in mapping.iteritems():
                if k.attrib.get('class') == 'dtreviewed':
                    extracted_dates.append(v.text)
                elif k.attrib.get('class') == 'description':
                    extracted_texts.append(v.text)

        # extract items are sorted in original order
        self.assertEquals(extracted_dates[0], '27-05-2014')
        self.assertEquals(extracted_dates[-1], '07-07-2013')
        self.assertEquals(extracted_texts[0], 'Kwaliteit van het eten matig')
        self.assertEquals(extracted_texts[-1], 'Paviljoen Strand 90 te Domburg is een uiterst sfeervol restaurant. De inrichting is smaakvol met mooie kleuren. De bediening is vriendelijk en behulpzaam. Het eten was lekker. Kortom, we zullen er zeker terug komen.')

if __name__ == '__main__':
    unittest.main()
