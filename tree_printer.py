from sql_ast import ASTNode, RootNode, FieldsNode, TablesNode, ConditionsNode, ValueNode, OperatorNode

class TreePrinter:
    """Визуализация AST-дерева"""

    @staticmethod
    def print_tree(node: ASTNode, prefix="", is_tail=True, is_root=True):
        branch = "└── " if is_tail else "├── "
        spacer = "    " if is_tail else "│   "

        if isinstance(node, ASTNode):
            node_str = node.node_type

            if is_root:
                print(node_str)
            else:
                print(prefix + branch + node_str)
        else:
            print(prefix + branch + str(node))
            return

        children = [child for child in node.children if isinstance(child, ASTNode)]

        if node.node_type in ['WHERE', 'CONDITIONS'] and not children:
            return

        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            TreePrinter.print_tree(child, prefix + spacer, is_last, is_root=False)