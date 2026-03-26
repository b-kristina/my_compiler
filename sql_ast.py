class ASTNode:
    """Базовый класс для всех узлов AST"""
    def __init__(self, node_type: str):
        self.node_type = node_type
        self.children = []

    def add_child(self, child):
        if child is not None:
            self.children.append(child)


class SelectStatement(ASTNode):
    """Узел: SELECT запрос"""
    def __init__(self, table, columns, where=None, order_by=None):
        super().__init__("SELECT STATEMENT")
        self.table = table
        self.columns = columns
        self.order_by = order_by
        if where:
            self.add_child(where)
        if order_by:
            self.add_child(order_by)


class WhereClause(ASTNode):
    """Узел: WHERE условие"""
    def __init__(self, condition):
        super().__init__("WHERE")
        self.add_child(condition)


class OrderByClause(ASTNode):
    """Узел: ORDER BY"""
    def __init__(self, column):
        super().__init__("ORDER BY")
        self.column = column


class BinaryCondition(ASTNode):
    """Узел: Условие сравнения (column operator value)"""
    def __init__(self, column, operator, value):
        super().__init__("CONDITION")
        self.column = column
        self.operator = operator
        self.value = value


class LogicalCondition(ASTNode):
    """Узел: Логическое условие (AND/OR)"""
    def __init__(self, operator, left, right):
        super().__init__(f"LOGIC ({operator})")
        self.add_child(left)
        self.add_child(right)