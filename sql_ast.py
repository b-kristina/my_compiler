class ASTNode:
    """Базовый класс для всех узлов AST"""
    def __init__(self, node_type: str):
        self.node_type = node_type
        self.children = []
        self.semantic_info = {}

    def add_child(self, child):
        if child is not None:
            self.children.append(child)


class RootNode(ASTNode):
    """Корневой узел дерева (Root)"""

    def __init__(self):
        super().__init__("       Root")
        self.select_keyword = KeywordNode("SELECT")
        self.fields_node = FieldsNode()
        self.from_keyword = KeywordNode("FROM")
        self.tables_node = TablesNode()
        self.where_keyword = KeywordNode("WHERE")
        self.conditions_node = ConditionsNode()
        self.group_by_node = GroupByClause(None)

        self.add_child(self.select_keyword)
        self.add_child(self.fields_node)
        self.add_child(self.from_keyword)
        self.add_child(self.tables_node)

    def add_where_clause(self, condition):
        """Добавляет WHERE и CONDITIONS только если есть условие"""
        if condition is not None:
            self.add_child(self.where_keyword)
            self.conditions_node.set_condition(condition)
            self.add_child(self.conditions_node)

    def add_group_by_clause(self, column):
        """Добавляет GROUP BY только если есть колонка"""
        if column is not None:
            self.group_by_node = GroupByClause(column)
            self.add_child(self.group_by_node)


class KeywordNode(ASTNode):
    """Узел для ключевых слов (SELECT, FROM, WHERE)"""
    def __init__(self, keyword: str):
        super().__init__(keyword)


class FieldsNode(ASTNode):
    """Узел для списка полей (FIELDS)"""
    def __init__(self):
        super().__init__("FIELDS")
        self.columns = []

    def add_column(self, column):
        self.columns.append(column)
        if isinstance(column, str):
            self.add_child(ValueNode(column))
        else:
            self.add_child(column)


class TablesNode(ASTNode):
    """Узел для списка таблиц (TABLES)"""
    def __init__(self):
        super().__init__("TABLES")
        self.tables = []

    def add_table(self, table: str):
        self.tables.append(table)
        self.add_child(ValueNode(table))


class ConditionsNode(ASTNode):
    """Узел для условий (CONDITIONS)"""
    def __init__(self):
        super().__init__("CONDITIONS")

    def set_condition(self, condition):
        if condition is not None:
            self.add_child(condition)


class GroupByClause(ASTNode):
    """Узел: GROUP BY"""
    def __init__(self, column):
        super().__init__("GROUP BY")
        self.column = column
        if column:
            self.add_child(ValueNode(column))


class ValueNode(ASTNode):
    """Узел для значений (колонки, таблицы, литералы)"""
    def __init__(self, value: str):
        super().__init__(value)
        self.value = value


class AggregateFunctionNode(ASTNode):
    """Узел для агрегатных функций (COUNT, SUM, AVG, MIN, MAX)"""
    def __init__(self, function_name: str, column: str):
        super().__init__(function_name)
        self.function_name = function_name
        self.column = column
        self.add_child(ValueNode(column))


class SelectStatement(ASTNode):
    """Узел: SELECT запрос"""
    def __init__(self, table, columns, where=None, order_by=None):
        super().__init__("SELECT STATEMENT")
        self.table = table
        self.columns = columns
        self.order_by = order_by
        self.column_types = {}
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
        self.column_type = None
        self.add_child(ValueNode(column))


class BinaryCondition(ASTNode):
    """Узел: Условие сравнения (column operator value)"""
    def __init__(self, column, operator, value):
        super().__init__(operator)
        self.column = column
        self.operator = operator
        self.value = value
        self.column_type = None
        self.value_type = None
        self.add_child(ValueNode(column))
        self.add_child(ValueNode(value))


class LogicalCondition(ASTNode):
    """Узел: Логическое условие (AND/OR)"""
    def __init__(self, operator, left, right):
        super().__init__(operator)
        self.operator = operator
        self.add_child(left)
        self.add_child(right)


class OperatorNode(ASTNode):
    """Узел для операторов сравнения и логических операторов"""
    def __init__(self, operator: str):
        super().__init__(operator)
        self.operator = operator