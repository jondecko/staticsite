import unittest

from textnode import TextType, TextNode, BlockType
from utils import text_node_to_html_node, split_nodes_delimiter
from utils import extract_markdown_images, extract_markdown_links
from utils import split_nodes_link, split_nodes_image
from utils import text_to_textnodes
from utils import markdown_to_blocks
from utils import block_to_block_type
from utils import markdown_to_html_node


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


    ### test for text_to_textnodes

    def test_for_text_to_textnodes(self):
        input = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        node = TextNode(input, TextType.TEXT,)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(text_to_textnodes(input), expected)

    def test_for_text_to_textnodes_with_empty_string(self):
        input = ""
        expected = []
        self.assertEqual(text_to_textnodes(input), expected)

    def test_for_text_to_textnodes_with_multiple_of_same_format_type(self):
        input = "Bold **one** and bold **two**."
        expected = [
            TextNode("Bold ", TextType.TEXT),
            TextNode("one", TextType.BOLD),
            TextNode(" and bold ", TextType.TEXT),
            TextNode("two", TextType.BOLD),
            TextNode(".", TextType.TEXT),
        ]
        self.assertEqual(text_to_textnodes(input), expected)


    ### test for markdown_to_blocks

    def test_for_markdown_to_blocks_verify_we_split_on_double_newline(self):
        input = "This is the first block\n\nThis is the second block"
        expected = [
            "This is the first block",
            "This is the second block",
        ]
        self.assertEqual(markdown_to_blocks(input), expected)

    def test_for_markdown_to_blocks_will_strip_leading_and_trailing_whitespace(self):
        input = "This is the first block \n\n This is the second block"
        expected = [
            "This is the first block",
            "This is the second block",
        ]
        self.assertEqual(markdown_to_blocks(input), expected)

    def test_for_markdown_to_blocks_will_remove_blank_blocks_due_to_excessive_newlines(self):
        input = "This is the first block\n\n\n\n\n\nThis is the second block"
        expected = [
            "This is the first block",
            "This is the second block",
        ]
        self.assertEqual(markdown_to_blocks(input), expected)

    def test_markdown_to_blocks_with_more_complex_input(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    ### test for block_to_block_type

    def test_block_to_block_type_defaults_to_a_normal_paragraph(self):
        input = "This is a block with no special block characters"
        self.assertEqual(block_to_block_type(input), BlockType.PARAGRAPH)

    def test_block_to_block_type_with_headings(self):
        input = "# A valid heading"
        self.assertEqual(block_to_block_type(input), BlockType.HEADING)
        input = "## A valid heading"
        self.assertEqual(block_to_block_type(input), BlockType.HEADING)
        input = "### A valid heading"
        self.assertEqual(block_to_block_type(input), BlockType.HEADING)
        input = "#### A valid heading"
        self.assertEqual(block_to_block_type(input), BlockType.HEADING)
        input = "##### A valid heading"
        self.assertEqual(block_to_block_type(input), BlockType.HEADING)
        input = "###### A valid heading"
        self.assertEqual(block_to_block_type(input), BlockType.HEADING)

    def test_block_to_block_type_with_invalid_heading_needs_space(self):
        input = "#An invalid heading, needs space after pound"
        self.assertEqual(block_to_block_type(input), BlockType.PARAGRAPH)

    def test_block_to_block_type_with_invalid_heading_7_or_more(self):
        input = "####### A valid heading"
        self.assertEqual(block_to_block_type(input), BlockType.PARAGRAPH)

    def test_block_to_block_type_with_code_blocks(self):
        input = "```This is a code block```"
        self.assertEqual(block_to_block_type(input), BlockType.CODE)

    def test_block_to_block_type_with_invalid_code_blocks(self):
        input = "``This is a code block```"
        self.assertEqual(block_to_block_type(input), BlockType.PARAGRAPH)

    def test_block_to_block_type_with_code_block_with_no_end_ticks(self):
        input = "```This is a code block"
        self.assertEqual(block_to_block_type(input), BlockType.PARAGRAPH)

    def test_block_to_block_type_with_quote(self):
        input = "> This is a valid quote"
        self.assertEqual(block_to_block_type(input), BlockType.QUOTE)
        input = ">This is also a valid quote"
        self.assertEqual(block_to_block_type(input), BlockType.QUOTE)

    def test_block_to_block_type_with_quote_on_multi_line(self):
        input = ">A valid quote\n>another valid quote\n> a third valid quote"
        self.assertEqual(block_to_block_type(input), BlockType.QUOTE)

    def test_block_to_block_type_with_invalid_quote_on_multi_line(self):
        input = ">A valid quote\n>another valid quote\n invalid third line no quote"
        self.assertEqual(block_to_block_type(input), BlockType.PARAGRAPH)

    def test_block_to_block_type_with_unordered_list(self):
        input = "- first ol list item"
        self.assertEqual(block_to_block_type(input), BlockType.UNORDERED_LIST)
        input = "- first ol list item\n- second ol list item"
        self.assertEqual(block_to_block_type(input), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_with_invalid_unordered_list(self):
        input = "- first ol list item\nthis is not a valid item"
        self.assertEqual(block_to_block_type(input), BlockType.PARAGRAPH)

    def test_block_to_block_type_with_ordered_list(self):
        input = "1. first ol list item"
        self.assertEqual(block_to_block_type(input), BlockType.ORDERED_LIST)
        input = "1. first ol list item\n2. second ol list item"
        self.assertEqual(block_to_block_type(input), BlockType.ORDERED_LIST)

    def test_block_to_block_type_with_invalid_ordered_list(self):
        input = "1. first ol list item\nthis is not a valid item"
        self.assertEqual(block_to_block_type(input), BlockType.PARAGRAPH)


    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>\nThis is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        md = """
# This is an h1

## This is an h2
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>This is an h1</h1><h2>This is an h2</h2></div>",
        )

    def test_quote(self):
        md = """
> The first quote

> The second quote
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>The first quote</blockquote><blockquote>The second quote</blockquote></div>",
        )


    def test_unordered_lists(self):
        md = """
- item one
- item two
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>item one</li><li>item two</li></ul></div>",
        )

    def test_ordered_lists(self):
        md = """
1. item one
2. item two
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>item one</li><li>item two</li></ol></div>",
        )

if __name__ == "__main__":
    unittest.main()
