import unittest

from leafnode import LeafNode 


class TestTextNode(unittest.TestCase):

    def test_creation_using_the_parent_constructor(self):
        node = LeafNode("p", "simple content")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "simple content")
        self.assertEqual(node.children, None)
        self.assertEqual(node.props, None)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")


    def test_leaf_to_html_no_value_raises_error(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()


    def test_leaf_to_html_no_tag_renders_text(self):
        node = LeafNode(None, "Hello, world!")
        self.assertEqual(node.to_html(), "Hello, world!")


    def test_leaf_to_html_working_with_an_a_tag(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        result = '<a href="https://www.google.com">Click me!</a>'
        self.assertEqual(node.to_html(), result)


if __name__ == "__main__":
    unittest.main()
