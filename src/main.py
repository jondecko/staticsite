import sys

from textnode import TextNode
from textnode import TextType
from utils import clear_public_directory
from utils import build_public_directory 
from utils import generate_page
from utils import generate_pages_recursive

def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"

    clear_public_directory('docs')
    build_public_directory('static', 'docs')
    generate_pages_recursive('content', 'template.html', 'docs', basepath)

main()
