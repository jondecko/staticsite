from textnode import TextNode
from textnode import TextType
from utils import clear_public_directory
from utils import build_public_directory 
from utils import generate_page

def main():
    clear_public_directory()
    build_public_directory()
    generate_page("content/index.md", "template.html", "public/index.html")


main()
