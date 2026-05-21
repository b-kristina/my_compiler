from __future__ import annotations

from sql_ast import AggregateFunctionNode, ASTNode, OperatorNode, OrderByClause, RootNode, ValueNode


class PythonCodeGenerator:
    """Генерирует исполняемый Python-код по AST SQL-запроса."""

    def generate(self, ast: RootNode) -> str:
        table_name = self._get_table_name(ast)
        columns = self._get_columns(ast)
        condition_expr = self._render_condition(ast.conditions_node.children[0]) if ast.conditions_node.children else None
        group_by_column = ast.group_by_node.column
        order_by_column = self._get_order_by_column(ast)
        has_aggregate = any(isinstance(column, AggregateFunctionNode) for column in columns)

        lines: list[str] = []
        lines.append("def execute(data):")
        lines.append(f"    rows = data.get({table_name!r}, [])[:]")

        if condition_expr:
            lines.append(f"    rows = [row for row in rows if {condition_expr}]")

        if order_by_column:
            lines.append(f"    rows = sorted(rows, key=lambda row: row.get({order_by_column!r}))")

        if has_aggregate:
            lines.extend(self._emit_aggregate_block(columns, group_by_column))
        elif group_by_column:
            lines.extend(self._emit_group_by_block(group_by_column))
        else:
            lines.extend(self._emit_projection_block(columns))

        return "\n".join(lines) + "\n"

    def execute(self, ast: RootNode, data: dict) -> list:
        source = self.generate(ast)
        namespace: dict[str, object] = {}
        exec(source, {}, namespace)
        return namespace["execute"](data)

    def _get_table_name(self, ast: RootNode) -> str:
        for child in ast.tables_node.children:
            if isinstance(child, ValueNode):
                return child.value
        raise ValueError("Не найдена таблица в AST")

    def _get_columns(self, ast: RootNode) -> list:
        return [child for child in ast.fields_node.children if isinstance(child, (ValueNode, AggregateFunctionNode))]

    def _get_order_by_column(self, ast: RootNode) -> str | None:
        for child in ast.children:
            if isinstance(child, OrderByClause):
                return child.column
        return None

    def _render_condition(self, node: ASTNode) -> str:
        if isinstance(node, OperatorNode):
            if node.operator in {"AND", "OR"}:
                left = self._render_condition(node.children[0])
                right = self._render_condition(node.children[1])
                return f"({left} {node.operator.lower()} {right})"

            left_value = node.children[0].value
            right_value = self._render_literal(node.children[1].value)
            operator = "==" if node.operator == "=" else node.operator
            return f"row.get({left_value!r}) {operator} {right_value}"

        raise ValueError(f"Неподдерживаемое условие: {type(node).__name__}")

    def _render_literal(self, value: str) -> str:
        if value.startswith("'") and value.endswith("'"):
            return repr(value[1:-1])
        if value.isdigit():
            return value
        return repr(value)

    def _emit_projection_block(self, columns: list) -> list[str]:
        if columns and isinstance(columns[0], ValueNode) and columns[0].value == "*":
            return ["    return rows"]

        selected_columns = [column.value for column in columns if isinstance(column, ValueNode)]
        mapping_parts = [f"{column!r}: row.get({column!r})" for column in selected_columns]
        lines = ["    result = []", "    for row in rows:"]
        lines.append(f"        result.append({{{', '.join(mapping_parts)}}})")
        lines.append("    return result")
        return lines

    def _emit_group_by_block(self, group_by_column: str) -> list[str]:
        return [
            "    groups = {}",
            "    for row in rows:",
            f"        key = row.get({group_by_column!r})",
            "        groups.setdefault(key, []).append(row)",
            "    result = []",
            "    for key in groups:",
            f"        result.append({{{group_by_column!r}: key}})",
            "    return result",
        ]

    def _emit_aggregate_block(self, columns: list, group_by_column: str | None) -> list[str]:
        lines = ["    result = []"]

        if group_by_column:
            lines.extend(
                [
                    "    groups = {}",
                    "    for row in rows:",
                    f"        key = row.get({group_by_column!r})",
                    "        groups.setdefault(key, []).append(row)",
                    "    for key, group_rows in groups.items():",
                    f"        row_result = {{{group_by_column!r}: key}}",
                ]
            )
            indent = "        "
            tail = ["        result.append(row_result)", "    return result"]
        else:
            lines.extend([
                "    group_rows = rows",
                "    row_result = {}",
            ])
            indent = "    "
            tail = ["    result.append(row_result)", "    return result"]

        for column in columns:
            if not isinstance(column, AggregateFunctionNode):
                continue

            func_name = column.function_name
            source_column = column.column
            key_name = func_name

            if func_name == "COUNT":
                if source_column == "*":
                    expr = "len(group_rows)"
                else:
                    expr = f"len([row for row in group_rows if row.get({source_column!r}) is not None])"
            elif func_name == "SUM":
                lines.append(f"{indent}values = [row.get({source_column!r}) for row in group_rows if row.get({source_column!r}) is not None]")
                expr = "sum(values) if values else 0"
            elif func_name == "AVG":
                lines.append(f"{indent}values = [row.get({source_column!r}) for row in group_rows if row.get({source_column!r}) is not None]")
                expr = "sum(values) / len(values) if values else 0"
            elif func_name == "MIN":
                lines.append(f"{indent}values = [row.get({source_column!r}) for row in group_rows if row.get({source_column!r}) is not None]")
                expr = "min(values) if values else None"
            elif func_name == "MAX":
                lines.append(f"{indent}values = [row.get({source_column!r}) for row in group_rows if row.get({source_column!r}) is not None]")
                expr = "max(values) if values else None"
            else:
                raise ValueError(f"Неподдерживаемая агрегатная функция: {func_name}")

            lines.append(f"{indent}row_result[{key_name!r}] = {expr}")

        lines.extend(tail)
        return lines