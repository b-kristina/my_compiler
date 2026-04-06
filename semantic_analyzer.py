from sql_ast import ASTNode, RootNode, FieldsNode, TablesNode, ConditionsNode, ValueNode, OperatorNode
from test_data import TEST_DATA, TABLE_SCHEMA

class SemanticError(Exception):
    pass

class SemanticAnalyzer:

    def __init__(self):
        self.tables = TEST_DATA
        self.schema = TABLE_SCHEMA
        self.errors = []

    def analyze(self, ast: RootNode) -> bool:
        """
        Выполняет семантический анализ AST-дерева
        Возвращает True если ошибок нет
        """
        self.errors = []

        table_name = None
        for child in ast.tables_node.children:
            if isinstance(child, ValueNode):
                table_name = child.value
                break

        if not self._check_table_exists(table_name):
            return False

        columns = []
        for child in ast.fields_node.children:
            if isinstance(child, ValueNode):
                columns.append(child.value)

        if not self._check_columns(columns, table_name):
            return False

        if ast.conditions_node.children:
            for child in ast.conditions_node.children:
                if isinstance(child, OperatorNode):
                    if not self._check_condition(child, table_name):
                        return False

        return len(self.errors) == 0

    def _check_table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы"""
        if table_name not in self.tables:
            self.errors.append(f"Таблица '{table_name}' не существует")
            return False
        return True

    def _check_column_exists(self, column: str, table_name: str) -> bool:
        """Проверяет существование колонки в таблице"""
        if column == '*':
            return True
        if table_name not in self.schema:
            return False
        if column not in self.schema[table_name]:
            self.errors.append(f"Колонка '{column}' не существует в таблице '{table_name}'")
            return False
        return True

    def _check_columns(self, columns: list, table_name: str) -> bool:
        """Проверяет все колонки в SELECT списке"""
        for col in columns:
            if not self._check_column_exists(col, table_name):
                return False
        return True

    def _check_condition(self, condition, table_name: str) -> bool:
        """Рекурсивная проверка условия WHERE"""
        if isinstance(condition, OperatorNode):
            if condition.operator in ['AND', 'OR']:
                left_ok = self._check_condition(condition.children[0], table_name)
                right_ok = self._check_condition(condition.children[1], table_name)
                return left_ok and right_ok
            else:
                col_name = condition.children[0].value
                if not self._check_column_exists(col_name, table_name):
                    return False

                col_type = self.schema[table_name].get(col_name)
                value = condition.children[1].value

                if col_type == 'integer':
                    if not value.isdigit() and not (value.startswith("'") and value.endswith("'")):
                        pass
                elif col_type == 'string':
                    if not value.startswith("'"):
                        self.errors.append(
                            f"Несоответствие типов: колонка '{col_name}' требует строку, "
                            f"получено {value}"
                        )
                        return False

                return True

        return True

    def get_errors(self) -> list:
        """Возвращает список ошибок"""
        return self.errors

    def get_column_types(self, table_name: str, columns: list) -> dict:
        """Возвращает типы колонок для AST"""
        types = {}
        if table_name in self.schema:
            for col in columns:
                if col == '*':
                    types['*'] = 'all'
                elif col in self.schema[table_name]:
                    types[col] = self.schema[table_name][col]
        return types