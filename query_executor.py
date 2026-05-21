from sql_ast import RootNode, FieldsNode, TablesNode, ConditionsNode, ValueNode, OperatorNode, AggregateFunctionNode, GroupByClause
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
        has_aggregate = False
        for child in ast.fields_node.children:
            if isinstance(child, ValueNode):
                columns.append(child.value)
            elif isinstance(child, AggregateFunctionNode):
                columns.append(child)
                has_aggregate = True

        group_by_column = None
        if ast.group_by_node.column:
            group_by_column = ast.group_by_node.column

        if has_aggregate:
            if group_by_column:
                return self._execute_aggregate_group_by(columns, rows, group_by_column)
            else:
                return self._execute_aggregate(columns, rows)

        if group_by_column:
            return self._execute_group_by(columns, rows, group_by_column)

        if columns == ['*']:
            return rows
        else:
            result = []
            for row in rows:
                filtered_row = {col: row.get(col) for col in columns}
                result.append(filtered_row)
            return result

    def _execute_group_by(self, columns: list, rows: list, group_by_column: str) -> list:
        """Выполняет группировку без агрегатов"""
        groups = {}
        for row in rows:
            key = row.get(group_by_column)
            if key not in groups:
                groups[key] = []
            groups[key].append(row)

        result = []
        for key, group_rows in groups.items():
            result.append({group_by_column: key})

        return result

    def _execute_aggregate_group_by(self, columns: list, rows: list, group_by_column: str) -> list:
        """Выполняет агрегатные функции с группировкой"""
        groups = {}
        for row in rows:
            key = row.get(group_by_column)
            if key not in groups:
                groups[key] = []
            groups[key].append(row)

        result = []
        for key, group_rows in groups.items():
            row_result = {group_by_column: key}

            for col in columns:
                if isinstance(col, AggregateFunctionNode):
                    func_name = col.function_name
                    column = col.column

                    if func_name == 'COUNT':
                        if column == '*':
                            row_result[f'{func_name}'] = len(group_rows)
                        else:
                            row_result[f'{func_name}'] = len([r for r in group_rows if r.get(column) is not None])
                    elif func_name == 'SUM':
                        values = [r.get(column) for r in group_rows if r.get(column) is not None]
                        row_result[f'{func_name}'] = sum(values) if values else 0
                    elif func_name == 'AVG':
                        values = [r.get(column) for r in group_rows if r.get(column) is not None]
                        row_result[f'{func_name}'] = sum(values) / len(values) if values else 0
                    elif func_name == 'MIN':
                        values = [r.get(column) for r in group_rows if r.get(column) is not None]
                        row_result[f'{func_name}'] = min(values) if values else None
                    elif func_name == 'MAX':
                        values = [r.get(column) for r in group_rows if r.get(column) is not None]
                        row_result[f'{func_name}'] = max(values) if values else None

            result.append(row_result)

        return result

    def _execute_aggregate(self, columns: list, rows: list) -> list:
        """Выполняет агрегатные функции"""
        result = {}

        for col in columns:
            if isinstance(col, AggregateFunctionNode):
                func_name = col.function_name
                column = col.column

                if func_name == 'COUNT':
                    if column == '*':
                        result[f'{func_name}'] = len(rows)
                    else:
                        result[f'{func_name}'] = len([r for r in rows if r.get(column) is not None])
                elif func_name == 'SUM':
                    values = [r.get(column) for r in rows if r.get(column) is not None]
                    result[f'{func_name}'] = sum(values) if values else 0
                elif func_name == 'AVG':
                    values = [r.get(column) for r in rows if r.get(column) is not None]
                    result[f'{func_name}'] = sum(values) / len(values) if values else 0
                elif func_name == 'MIN':
                    values = [r.get(column) for r in rows if r.get(column) is not None]
                    result[f'{func_name}'] = min(values) if values else None
                elif func_name == 'MAX':
                    values = [r.get(column) for r in rows if r.get(column) is not None]
                    result[f'{func_name}'] = max(values) if values else None

        return [result]

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