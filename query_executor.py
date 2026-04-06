from sql_ast import RootNode, FieldsNode, TablesNode, ConditionsNode, ValueNode, OperatorNode
from test_data import TEST_DATA

class QueryExecutor:

    def __init__(self):
        self.data = TEST_DATA

    def execute(self, ast: RootNode) -> list:
        table_name = None
        for child in ast.tables_node.children:
            if isinstance(child, ValueNode):
                table_name = child.value
                break

        if table_name not in self.data:
            return []

        rows = self.data[table_name][:]

        condition = None
        for child in ast.conditions_node.children:
            if isinstance(child, OperatorNode):
                condition = child
                break

        if condition:
            rows = [row for row in rows if self._evaluate_condition(condition, row)]

        columns = []
        for child in ast.fields_node.children:
            if isinstance(child, ValueNode):
                columns.append(child.value)

        if columns == ['*']:
            return rows
        else:
            result = []
            for row in rows:
                filtered_row = {col: row.get(col) for col in columns}
                result.append(filtered_row)
            return result

    def _evaluate_condition(self, condition, row: dict) -> bool:
        """Вычисляет условие WHERE для одной строки"""
        if isinstance(condition, OperatorNode):
            if condition.operator in ['AND', 'OR']:
                left = self._evaluate_condition(condition.children[0], row)
                right = self._evaluate_condition(condition.children[1], row)

                if condition.operator == 'AND':
                    return left and right
                elif condition.operator == 'OR':
                    return left or right
            else:
                col_value = row.get(condition.children[0].value)
                cmp_value = condition.children[1].value

                if cmp_value.startswith("'") and cmp_value.endswith("'"):
                    cmp_value = cmp_value[1:-1]
                elif cmp_value.isdigit():
                    cmp_value = int(cmp_value)

                if condition.operator == '=':
                    return col_value == cmp_value
                elif condition.operator == '>':
                    return col_value > cmp_value
                elif condition.operator == '<':
                    return col_value < cmp_value
                elif condition.operator == '>=':
                    return col_value >= cmp_value
                elif condition.operator == '<=':
                    return col_value <= cmp_value
                elif condition.operator == '!=':
                    return col_value != cmp_value

        return True

    def print_results(self, results: list):
        if not results:
            print("   (пустой результат)")
            return

        columns = list(results[0].keys())
        widths = {col: len(col) for col in columns}
        for row in results:
            for col in columns:
                widths[col] = max(widths[col], len(str(row[col])))

        header = " | ".join(col.ljust(widths[col]) for col in columns)
        print("   " + header)
        print("   " + "-" * len(header))

        for row in results:
            line = " | ".join(str(row[col]).ljust(widths[col]) for col in columns)
            print("   " + line)

        print(f"\n   Всего строк: {len(results)}")