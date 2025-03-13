from textnode import TextNode
from textnode import TextType
from utils import clear_public_directory
from utils import build_public_directory 
from utils import generate_page

def main():
    clear_public_directory()
    build_public_directory()
    generate_page("content/index.md", "template.html", "public/index.html")
    generate_page("content/contact/index.md", "template.html", "public/contact/index.html")                     #TODO: fix the bug in this file
    generate_page("content/blog/glorfindel/index.md", "template.html", "public/blog/glorfindel/index.html")
    #generate_page("content/blog/majesty/index.md", "template.html", "public/blog/majesty/index.html")
    #generate_page("content/blog/tom/index.md", "template.html", "public/blog/tom/index.html")

main()
