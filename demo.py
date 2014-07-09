# -*- coding: utf-8 -*-
import sys
import json
import random
import operator

from lxml.html import document_fromstring
from lxml import etree
from lxml.html import tostring

from mdr.mdr import MDR
from mdr.utils import simplify_xpath

if __name__ == '__main__':

    html = open(sys.argv[1]).read()

    mdr = MDR()
    candidates, doc = mdr.list_candidates(html)

    mappings, reverse_mappings, _ = mdr.extract(candidates[0])
    colors = ['#FF0000', '#00FF00', '#0000F',F '#FFFF00', '#00FFFF', '#FF00FF']

    # XXX: not working
    for candidate in candidates:
        candidate.attrib['style'] = 'border-style: thin solid yellow;'

    for item, seed_item in reverse_mappings.iteritems():
        template_attr = item.attrib.get('data-scrapy-annotate')
        if template_attr:
            unescaped = template_attr.replace('&quot;', '"')
            annotation = json.loads(unescaped)
            print annotation
            color = random.choice(colors)
            colors.remove(color)
            for tree, mapping in mappings.iteritems():
                if item != mapping.get(seed_item) and mapping.get(seed_item) != None:
                    mapping.get(seed_item).attrib['style'] = 'background-color:%s' % color
            if seed_item != None:
                item.attrib['style'] = 'background-color:%s ; border-style: dashed;' % color

    with open(sys.argv[2], 'w') as f:
        print >>f, tostring(doc)