def _traverse_tree(self, node, parent, chunks, content):
        if node.type in ['function_definition', 'class_definition']:
            chunk = ChunkNode(
                id = f"{node.type}_{node.start_point[0]}_{node.end_point[0]}",
                type = 'function' if node.type == 'function_definition' else 'class',
                name = self._get_node_name(node),
                content = content[node.start_byte:node.end_byte],
                start_line = node.start_point[0],
                end_line = node.end_point[0],
                parent = parent
            )

            chunks.append(chunk)
            parent = chunk

        for child in node.children:
            self._traverse_tree(child, parent, chunks, content)