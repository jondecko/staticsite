import re

from parentnode import ParentNode
from leafnode import LeafNode 
from htmlnode import HTMLNode
from textnode import TextType, TextNode, BlockType


def text_node_to_html_node(text_node):
    match(text_node.text_type):
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"src": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})

    node = HTMLNode()
    return node


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        parts = old_node.text.split(delimiter)

        if len(parts) == 1:
            new_nodes.append(old_node)
            continue
        
        if len(parts) % 2 == 0:
            raise Exception(f"delimiter of {delimiter} starts but does not end")
        
        new_nodes.append(TextNode(parts[0], TextType.TEXT))
        
        for i in range(1, len(parts), 2):
            new_nodes.append(TextNode(parts[i], text_type))
            if i + 1 < len(parts):
                new_nodes.append(TextNode(parts[i+1], TextType.TEXT))
    
    return new_nodes


def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        images = extract_markdown_images(node.text)

        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        if not images:
            new_nodes.append(TextNode(node.text, TextType.TEXT))
            continue

        text_to_split = node.text
        for image in images:
            temp = f"![{image[0]}]({image[1]})"
            sections = text_to_split.split(temp, 1)

            if sections[0] == "":
                new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            else:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
                new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            text_to_split = sections[1]

        if text_to_split:
            new_nodes.append(TextNode(text_to_split, TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
        links = extract_markdown_links(node.text)

        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        if not links:
            new_nodes.append(TextNode(node.text, TextType.TEXT))
            continue

        text_to_split = node.text
        for link in links:
            temp = f"[{link[0]}]({link[1]})"
            sections = text_to_split.split(temp, 1)

            if sections[0] == "":
                new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            else:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
                new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            text_to_split = sections[1]

        if text_to_split:
            new_nodes.append(TextNode(text_to_split, TextType.TEXT))

    return new_nodes


def text_to_textnodes(text):
    if not text: return []

    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    return nodes


def markdown_to_blocks(markdown):
    blocks = markdown.split('\n\n')
    blocks = map(lambda x: x.strip(), blocks)
    blocks = filter(lambda x: x != '', blocks)
    return list(blocks)

def block_to_block_type(text_block):
    if text_block[0] == "#":
        sections = text_block.split(" ")
        if len(sections[0]) <= 6 and all(map(lambda x: x == "#", sections[0])):
            return BlockType.HEADING
    elif text_block[0] == "`":
        sections = text_block.split("```")
        if len(sections) == 3 and sections[0] == "" and sections[2] == "":
            return BlockType.CODE
    elif text_block[0] == ">":
        sections = text_block.split("\n")
        if all(map(lambda x: x[0] == ">", sections)):
            return BlockType.QUOTE
    elif text_block[0] == "-":
        sections = text_block.split("\n")
        if all(map(lambda x: x[0:2] == "- ", sections)):
            return BlockType.UNORDERED_LIST
    elif text_block[0] in "123456789":
        sections = text_block.split("\n")
        for index, section in enumerate(sections):
            x = section.split(".")
            if len(x) == 2 and int(x[0]) == index + 1:
                continue 
            else:
                return BlockType.PARAGRAPH
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH













