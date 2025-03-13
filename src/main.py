from textnode import TextNode
from textnode import TextType
from utils import clear_public_directory
from utils import build_public_directory 
from utils import generate_page
from utils import generate_pages_recursive

def main():
    clear_public_directory()
    build_public_directory()
    generate_pages_recursive('content', 'template.html', 'public')

main()
