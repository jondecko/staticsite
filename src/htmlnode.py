class HTMLNode():

    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props


    def to_html(self):
        raise NotImplementedError()


    def props_to_html(self):
        prop_str = ""
        for prop_key in self.props:
            f = prop_key + "=" + '"' + self.props[prop_key] + '"' + " "
            prop_str += f
        return prop_str.strip()


    def __repr__(self):
        return f"{self.tag}, {self.value}, {self.children}, {self.props}"
