import unittest

from lxml import etree
from mdr._tree import _simple_tree_match
from mdr.tree import clustered_tree_match

s1 = """<root>
            <b>
                <d></d>
                <e></e>
            </b>
            <c>
                <f></f>
            </c>
            <b>
                <e></e>
                <d></d>
            </b>
            <c>
                <g>
                    <h></h>
                    <i></i>
                    <j></j>
                </g>
            </c>
        </root>
"""

s2 = """<root>
            <b>
                <d></d>
                <e></e>
            </b>
            <c>
                <g>
                    <h></h>
                </g>
                <f></f>
            </c>
        </root>
"""

class TreeMatchTest(unittest.TestCase):

    def test_tree_match(self):
        tree1 = etree.XML(s1)
        tree2 = etree.XML(s2)
        self.assertEquals(7, _simple_tree_match(tree1, tree2))
        self.assertEquals(0.375, clustered_tree_match(tree1, tree2))

