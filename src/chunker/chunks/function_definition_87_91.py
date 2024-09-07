def _get_node_name(self, node):
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decoder('utf-8')
        return "Unknown"