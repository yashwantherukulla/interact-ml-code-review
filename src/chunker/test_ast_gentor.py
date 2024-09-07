import msgpack

example_ast = {
    'type': 'module',
    'start_point': (0, 0),
    'end_point': (7, 0),
    'children': [
        {
            'type': 'function_definition',
            'start_point': (0, 0),
            'end_point': (6, 0),
            'children': [
                {
                    'type': 'def',
                    'start_point': (0, 0),
                    'end_point': (0, 3)
                },
                {
                    'type': 'identifier',
                    'start_point': (0, 4),
                    'end_point': (0, 18)
                },
                {
                    'type': 'parameters',
                    'start_point': (0, 18),
                    'end_point': (0, 24),
                    'children': [
                        {
                            'type': 'identifier',
                            'start_point': (0, 19),
                            'end_point': (0, 23)
                        }
                    ]
                },
                {
                    'type': 'block',
                    'start_point': (1, 4),
                    'end_point': (6, 0),
                    'children': [
                        {
                            'type': 'if_statement',
                            'start_point': (1, 4),
                            'end_point': (5, 12),
                            'children': [
                                {
                                    'type': 'if',
                                    'start_point': (1, 4),
                                    'end_point': (1, 6)
                                },
                                {
                                    'type': 'comparison_operator',
                                    'start_point': (1, 7),
                                    'end_point': (1, 16)
                                },
                                {
                                    'type': 'block',
                                    'start_point': (2, 8),
                                    'end_point': (3, 21),
                                    'children': [
                                        {
                                            'type': 'return_statement',
                                            'start_point': (2, 8),
                                            'end_point': (2, 19)
                                        }
                                    ]
                                },
                                {
                                    'type': 'else',
                                    'start_point': (3, 4),
                                    'end_point': (3, 8)
                                },
                                {
                                    'type': 'block',
                                    'start_point': (4, 8),
                                    'end_point': (5, 12),
                                    'children': [
                                        {
                                            'type': 'return_statement',
                                            'start_point': (4, 8),
                                            'end_point': (4, 20)
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

with open('example_ast.msgpack', 'wb') as f:
    msgpack.pack(example_ast, f)

print("Example AST file created: example_ast.msgpack")