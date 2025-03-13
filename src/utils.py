import re
import os
import shutil

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
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", text_node.text, {"src": text_node.url, "alt": text_node.text})

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
        
        if parts[0] == "":  #this is when we split and delim is at beginning 
            new_nodes.append(TextNode(parts[1], text_type))
            for i in range(2, len(parts), 2):
                new_nodes.append(TextNode(parts[i], TextType.TEXT))
        else:
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


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    parent_node = ParentNode("div", [], )

    for block in blocks:
        block_type = block_to_block_type(block)
        block_node = None

        match(block_type):
            case BlockType.PARAGRAPH:
                clean_block = block.replace('\n', ' ')
                children = text_to_children(clean_block)
                block_node = ParentNode("p", children, )
            case BlockType.HEADING:
                sections = block.split(" ", 1)
                hvalue = len(sections[0])
                heading_text = sections[1]
                children = text_to_children(heading_text)
                block_node = ParentNode(f"h{hvalue}", children)
            case BlockType.CODE:
                clean_block = block.replace('```', '')
                block_node = ParentNode("pre", [])
                block_node.children.append(LeafNode("code", clean_block, []))
            case BlockType.QUOTE:
                clean_block = block.replace('\n', ' ').replace('> ', '')
                children = text_to_children(clean_block)
                block_node = ParentNode("blockquote", children, )
            case BlockType.UNORDERED_LIST:
                clean_block = block.replace('- ', '')
                children = []
                block_node = ParentNode("ul", children, )
                for li_content in clean_block.split('\n'):
                    children = text_to_children(li_content)
                    block_node.children.append(ParentNode("li", children))
            case BlockType.ORDERED_LIST:
                children = []
                block_node = ParentNode("ol", children, )
                for li_content in block.split('\n'):
                    children = text_to_children(li_content.split(" ", 1)[1])
                    block_node.children.append(ParentNode("li", children))

        if block_node:
            parent_node.children.append(block_node)

    return parent_node


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        html_nodes.append(html_node)
    return html_nodes


def clear_public_directory(dir_to_remove="./public"):
    print("STARTED - clear_public_directory")
    if os.path.exists(dir_to_remove):
        print(f"REMOVING - {dir_to_remove}")
        shutil.rmtree(dir_to_remove)
    else:
        print(f"NOOP - {dir_to_remove} did not exist")


def build_public_directory(dir_to_build_from="./static", dir_to_build_to="./public"):
    print("STARTED - build_public_directory")
    if not os.path.exists(dir_to_build_to):
        print(f"CREATING - {dir_to_build_to}")
        os.mkdir(dir_to_build_to)

    dirs = os.listdir(dir_to_build_from)
    for dir in dirs:
        path_from = os.path.join(dir_to_build_from, dir)
        path_to = os.path.join(dir_to_build_to, dir)
        if os.path.isdir(path_from):
            print(f"CREATING - {path_to}")
            os.mkdir(path_to)
            build_public_directory(path_from, path_to)
        else:
            print(f"COPY - {path_from} TO {path_to}")
            shutil.copy(path_from, path_to)


def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block_to_block_type(block) == BlockType.HEADING:
            sections = block.split(" ", 1)
            if len(sections[0]) == 1:
                return sections[1]
    raise Exception("no title to extract")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    from_file = open(from_path, "r")
    md = from_file.read()
    from_file.close()

    template_file = open(template_path, "r")
    template = template_file.read()
    template_file.close()

    html_node = markdown_to_html_node(md)

    title = extract_title(md)
    html_string = html_node.to_html()

    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html_string)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    dest_file = open(dest_path, "a")
    dest_file.write(template)
    dest_file.close()
