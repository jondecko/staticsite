import unittest

from parentnode import ParentNode
from leafnode import LeafNode 


class TestParentNode(unittest.TestCase):

    def test_parent_to_html_no_tag_raises_error(self):
        child = LeafNode("p", "Hello, world!")
        node = ParentNode("", [child])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_to_html_no_children_raises_error(self):
        node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_to_html_none_children_raises_error(self):
        node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_to_html_with_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        expected = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(node.to_html(), expected)

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_a_mix_at_child_layer(self):
        grandchild_node = LeafNode("b", "grandchild")
        random_leaf = LeafNode("b", "rando")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node, random_leaf])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span><b>rando</b></div>",
        )


if __name__ == "__main__":
    unittest.main()
