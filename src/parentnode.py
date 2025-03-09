from htmlnode import HTMLNode

class ParentNode(HTMLNode):

    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    
    def to_html(self):
        if not self.tag:
            raise ValueError("no tag provided")
        if not self.children:
            raise ValueError("no children provided")

        html = f"<{self.tag}"
        if self.props: 
            html += f" {self.props_to_html()}"
        html += ">"
        for child in self.children:
            html += child.to_html()
        html += f"</{self.tag}>"
        return html
