from sql_ast import ASTNode


class TreePrinter:
    """Визуализация AST-дерева"""

    @staticmethod
    def print_tree(node: ASTNode, prefix="", is_tail=True):

        branch = "└── " if is_tail else "├── "
        spacer = "    " if is_tail else "│   "

        if isinstance(node, ASTNode):
            node_str = node.node_type

            if hasattr(node, 'table'):
                node_str += f" [Table: {node.table}]"
            if hasattr(node, 'columns'):
                node_str += f" [{', '.join(node.columns)}]"
            if hasattr(node, 'column') and not hasattr(node, 'columns'):
                node_str += f" [{node.column}]"
            if hasattr(node, 'operator'):
                node_str += f" [{node.operator}]"
            if hasattr(node, 'value'):
                node_str += f" [{node.value}]"

            print(prefix + branch + node_str)
        else:
            print(prefix + branch + str(node))
            return

        children = node.children
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            TreePrinter.print_tree(child, prefix + spacer, is_last)