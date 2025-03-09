import unittest

from textnode import TextType, TextNode
from utils import text_node_to_html_node, split_nodes_delimiter
from utils import extract_markdown_images, extract_markdown_links
from utils import split_nodes_link, split_nodes_image


class TestUtils(unittest.TestCase):

    ### test for text_node_to_html_node
    
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a bold node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a bold node")

    def test_italic(self):
        node = TextNode("This is an italic node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is an italic node")

    def test_code(self):
        node = TextNode("This is a code node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a code node")

    def test_link(self):
        node = TextNode("Click Me", TextType.LINK, url="google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click Me")
        self.assertEqual(html_node.props["src"], "google.com")

    def test_img(self):
        node = TextNode("this image is cool", TextType.IMAGE, url="cool.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, None)
        self.assertEqual(html_node.props["src"], "cool.jpg")
        self.assertEqual(html_node.props["alt"], "this image is cool")

    ### test for split_nodes_delimiter

    def test_split_nodes_non_text_type(self):
        node = TextNode("This is text with a `code block` word", TextType.CODE)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a `code block` word", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_with_no_delimiter(self):
        node = TextNode("This is text with a code block word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a code block word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_with_one_delimiter(self):
        node = TextNode("This is text with a `code block word", TextType.TEXT)
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(str(context.exception), "delimiter of ` starts but does not end")

    def test_split_nodes_code_blocks(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_italic_blocks(self):
        node = TextNode("This is text with an _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_bold_blocks(self):
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_with_multiple_blocks_in_same_node(self):
        text = "This is text with `one code block` and then some more text and `another code block`"
        node = TextNode(text, TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with ", TextType.TEXT),
            TextNode("one code block", TextType.CODE),
            TextNode(" and then some more text and ", TextType.TEXT),
            TextNode("another code block", TextType.CODE),
            TextNode("", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    ### test for extract_markdown_images

    def test_extracting_markdown_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
        self.assertEqual(extract_markdown_images(text), expected)


    ### test for extract_markdown_links

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        expected = [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
        self.assertEqual(extract_markdown_links(text), expected)


    ### test for split_nodes_link

    def test_for_split_nodes_link_with_no_links(self):
        node = TextNode("No links here", TextType.TEXT,)
        expected = [ TextNode("No links here", TextType.TEXT) ]
        self.assertEqual(split_nodes_link([node]), expected)


    def test_for_split_nodes_link_with_no_links_twice(self):
        node1 = TextNode("No links here", TextType.TEXT,)
        node2 = TextNode("Still no links here", TextType.TEXT,)
        expected = [ 
            TextNode("No links here", TextType.TEXT),
            TextNode("Still no links here", TextType.TEXT,)
        ]
        self.assertEqual(split_nodes_link([node1, node2]), expected)

    def test_for_split_nodes_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertEqual(split_nodes_link([node]), expected)

    def test_for_split_nodes_link_only_with_links(self):
        node = TextNode(
            "[to boot dev](https://www.boot.dev)[to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        expected = [
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertEqual(split_nodes_link([node]), expected)

    def test_for_split_nodes_link_with_no_text_between_links(self):
        node = TextNode(
            "No text between links [to boot dev](https://www.boot.dev)[to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        expected = [
            TextNode("No text between links ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertEqual(split_nodes_link([node]), expected)

    def test_for_split_nodes_link_with_text_at_end(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev) with text at end",
            TextType.TEXT,
        )
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            TextNode(" with text at end", TextType.TEXT),
        ]
        self.assertEqual(split_nodes_link([node]), expected)

    def test_for_split_nodes_link_with_empty_input(self):
        node = TextNode("", TextType.TEXT,)
        expected = [TextNode("", TextType.TEXT,)]
        self.assertEqual(split_nodes_link([node]), expected)

    ### test for split_nodes_image

    def test_for_split_nodes_image_with_no_image(self):
        node = TextNode("No image here", TextType.TEXT,)
        expected = [ TextNode("No image here", TextType.TEXT) ]
        self.assertEqual(split_nodes_image([node]), expected)


    def test_for_split_nodes_image_with_no_images_twice(self):
        node1 = TextNode("No image here", TextType.TEXT,)
        node2 = TextNode("Still no image here", TextType.TEXT,)
        expected = [ 
            TextNode("No image here", TextType.TEXT),
            TextNode("Still no image here", TextType.TEXT,)
        ]
        self.assertEqual(split_nodes_image([node1, node2]), expected)

    def test_for_split_nodes_image(self):
        node = TextNode(
            "This is text with an image ![doggy](doggy.jpg) and ![kitty](kitty.jpg)",
            TextType.TEXT,
        )
        expected = [
            TextNode("This is text with an image ", TextType.TEXT),
            TextNode("doggy", TextType.IMAGE, "doggy.jpg"),
            TextNode(" and ", TextType.TEXT),
            TextNode("kitty", TextType.IMAGE, "kitty.jpg"),
        ]
        self.assertEqual(split_nodes_image([node]), expected)

    def test_for_split_nodes_image_with_only_image(self):
        node = TextNode("![doggy](doggy.jpg)![kitty](kitty.jpg)", TextType.TEXT,)
        expected = [
            TextNode("doggy", TextType.IMAGE, "doggy.jpg"),
            TextNode("kitty", TextType.IMAGE, "kitty.jpg"),
        ]
        self.assertEqual(split_nodes_image([node]), expected)

    def test_for_split_nodes_image_with_no_text_between_images(self):
        node = TextNode(
            "No text between images ![doggy](doggy.jpg)![kitty](kitty.jpg)",
            TextType.TEXT,
        )
        expected = [
            TextNode("No text between images ", TextType.TEXT),
            TextNode("doggy", TextType.IMAGE, "doggy.jpg"),
            TextNode("kitty", TextType.IMAGE, "kitty.jpg"),
        ]
        self.assertEqual(split_nodes_image([node]), expected)

    def test_for_split_nodes_image_with_text_at_end(self):
        node = TextNode(
            "This is text with an image ![doggy](doggy.jpg) with text at end",
            TextType.TEXT,
        )
        expected = [
            TextNode("This is text with an image ", TextType.TEXT),
            TextNode("doggy", TextType.IMAGE, "doggy.jpg"),
            TextNode(" with text at end", TextType.TEXT),
        ]
        self.assertEqual(split_nodes_image([node]), expected)

    def test_for_split_nodes_image_with_empty_input(self):
        node = TextNode("", TextType.TEXT,)
        expected = [TextNode("", TextType.TEXT,)]
        self.assertEqual(split_nodes_image([node]), expected)


if __name__ == "__main__":
    unittest.main()
