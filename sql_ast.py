class ASTNode:
    """Базовый класс для всех узлов AST"""
    def print_tree(self, indent=0):
        raise NotImplementedError

class SelectStatement(ASTNode):
    def __init__(self, columns, table, where=None, order_by=None):
        self.columns = columns  # список строк или '*'
        self.table = table      # имя таблицы
        self.where = where      # узел условия или None
        self.order_by = order_by  # имя колонки или None

    def print_tree(self, indent=0):
        print(" " * indent + "SELECT STATEMENT")
        print(" " * (indent + 2) + f"Table: {self.table}")
        print(" " * (indent + 2) + f"Columns: {', '.join(self.columns)}")
        if self.where:
            print(" " * (indent + 2) + "WHERE:")
            self.where.print_tree(indent + 4)
        if self.order_by:
            print(" " * (indent + 2) + f"ORDER BY: {self.order_by}")

class BinaryCondition(ASTNode):
    """Условие: column operator value"""
    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value

    def print_tree(self, indent=0):
        print(" " * indent + f"CONDITION: {self.column} {self.operator} {self.value}")

class LogicalCondition(ASTNode):
    """Логическое условие: left AND/OR right"""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def print_tree(self, indent=0):
        print(" " * indent + f"LOGIC: {self.operator}")
        self.left.print_tree(indent + 2)
        self.right.print_tree(indent + 2)