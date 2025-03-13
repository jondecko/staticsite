import sys

from textnode import TextNode
from textnode import TextType
from utils import clear_public_directory
from utils import build_public_directory 
from utils import generate_page
from utils import generate_pages_recursive

def main():
    basepath = '/'
    for arg in sys.argv:
        parts = arg.split('=')
        if parts[0] == 'basepath': 
            basepath = parts[1]

    clear_public_directory('docs')
    build_public_directory('static', 'docs')
    generate_pages_recursive('content', 'template.html', 'docs', basepath)

main()
