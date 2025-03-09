import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_rpr(self):
        node = HTMLNode("p", "simple content")
        expected = "p, simple content, None, None"
        self.assertEqual(str(node), expected)

    def test_props_to_html_with_none_props(self):
        props = {}
        node = HTMLNode("p", "simple content", None, props)
        expected = '' 
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_with_empty_props(self):
        props = {}
        node = HTMLNode("p", "simple content", None, props)
        expected = '' 
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_with_one_element(self):
        props = {"prop1": "value1"}
        node = HTMLNode("p", "simple content", None, props)
        expected = 'prop1="value1"' 
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_with_two_elements(self):
        props = {"prop1": "value1", "prop2": "value2"}
        node = HTMLNode("p", "simple content", None, props)
        expected = 'prop1="value1" prop2="value2"' 
        self.assertEqual(node.props_to_html(), expected)


if __name__ == "__main__":
    unittest.main()
