from parser_base import BaseParser, ParsingError
from sql_ast import (
    RootNode, FieldsNode, TablesNode, ConditionsNode,
    ValueNode, OperatorNode,
    WhereClause, OrderByClause,
    BinaryCondition, LogicalCondition
)

class SqlParser(BaseParser):

    def __init__(self, text: str):
        super().__init__(text)

    def parse_identifier(self) -> str:
        """
        IDENTIFIER -> [a-zA-Z_][a-zA-Z0-9_]*
        """
        self.ws()
        result = ''
        if self.curr.isalpha() or self.curr == '_':
            result += self.curr
            self.pos += 1
            while self.curr.isalnum() or self.curr == '_':
                result += self.curr
                self.pos += 1
        else:
            raise ParsingError(f'Ожидается идентификатор, найдено: {self.curr}')
        self.ws()
        return result

    def parse_number(self) -> str:
        """
        NUMBER -> [0-9]+
        """
        self.ws()
        result = ''
        while self.curr.isdigit():
            result += self.curr
            self.pos += 1
        if not result:
            raise ParsingError(f'Ожидается число, найдено: {self.curr}')
        self.ws()
        return result

    def parse_string(self) -> str:
        """
        STRING -> '...'
        """
        self.ws()
        if self.curr == "'":
            self.pos += 1
            result = ''
            while self.curr != "'" and self.curr != '$':
                result += self.curr
                self.pos += 1
            if self.curr != "'":
                raise ParsingError('Незакрытая строка')
            self.pos += 1
            self.ws()
            return "'" + result + "'"
        else:
            raise ParsingError(f'Ожидается строка, найдено: {self.curr}')

    def parse_select_list(self):
        """
        selectList -> '*' | column (',' column)*
        """
        self.ws()
        if self.curr == '*':
            self.pos += 1
            self.ws()
            return ['*']

        columns = [self.parse_identifier()]
        while self.is_parse(','):
            self.parse(',')
            columns.append(self.parse_identifier())
        return columns

    def parse_table_name(self) -> str:
        """
        tableName -> IDENTIFIER
        """
        return self.parse_identifier()

    def parse_comparison_operator(self) -> str:
        """
        comparisonOperator -> '=' | '>' | '<' | '>=' | '<=' | '!='
        """
        self.ws()
        # сначала двухсимвольные операторы
        two_char_ops = ['>=', '<=', '!=']
        for op in two_char_ops:
            if self.text[self.pos:self.pos + 2] == op:
                self.pos += 2
                self.ws()
                return op

        # односимвольные
        one_char_ops = ['=', '>', '<']
        for op in one_char_ops:
            if self.curr == op:
                self.pos += 1
                self.ws()
                return op

        raise ParsingError(f'Ожидается оператор сравнения, найдено: {self.curr}')

    def parse_value(self) -> str:
        """
        value -> IDENTIFIER | NUMBER | STRING
        """
        self.ws()
        if self.curr == "'":
            return self.parse_string()
        elif self.curr.isdigit():
            return self.parse_number()
        elif self.curr.isalpha() or self.curr == '_':
            return self.parse_identifier()
        else:
            raise ParsingError(f'Ожидается значение, найдено: {self.curr}')

    def _is_logical_operator(self) -> bool:
        """
        Проверка на AND/OR с границей слова
        (чтобы ORDER не распознавался как OR)
        """
        self.ws()
        pos = self.pos

        # проверка AND
        if self.text[pos:pos + 3] == 'AND':
            next_char = self.text[pos + 3] if pos + 3 < len(self.text) else '$'
            if not next_char.isalnum() and next_char != '_':
                return True

        # проверка OR
        if self.text[pos:pos + 2] == 'OR':
            next_char = self.text[pos + 2] if pos + 2 < len(self.text) else '$'
            if not next_char.isalnum() and next_char != '_':
                return True

        return False

    def _parse_logical_operator(self) -> str:
        """
        Парсинг AND/OR с границей слова
        """
        self.ws()
        pos = self.pos

        # проверка AND
        if self.text[pos:pos + 3] == 'AND':
            next_char = self.text[pos + 3] if pos + 3 < len(self.text) else '$'
            if not next_char.isalnum() and next_char != '_':
                self.pos = pos + 3
                self.ws()
                return 'AND'

        # проверка OR
        if self.text[pos:pos + 2] == 'OR':
            next_char = self.text[pos + 2] if pos + 2 < len(self.text) else '$'
            if not next_char.isalnum() and next_char != '_':
                self.pos = pos + 2
                self.ws()
                return 'OR'

        raise ParsingError(f'Ожидается AND или OR, найдено: {self.curr}')

    def parse_condition(self):
        """
        condition -> '(' condition ')'
                  | condition AND condition
                  | condition OR condition
                  | column comparisonOperator value
        """
        self.ws()

        # скобки: '(' condition ')'
        if self.curr == '(':
            self.pos += 1
            result = self.parse_condition()
            self.parse(')')
            return result

        # левая часть: column
        left_col = self.parse_identifier()

        # оператор сравнения
        self.ws()
        if self.is_parse('=', '>', '<', '!', '>'):
            op = self.parse_comparison_operator()
            value = self.parse_value()
            result = OperatorNode(op)
            result.add_child(ValueNode(left_col))
            result.add_child(ValueNode(value))
        else:
            raise ParsingError(f'Ожидается оператор условия, найдено: {self.curr}')

        # проверяем AND/OR
        self.ws()
        if self._is_logical_operator():
            logical_op = self._parse_logical_operator()
            right = self.parse_condition()
            logic_node = OperatorNode(logical_op)
            logic_node.add_child(result)
            logic_node.add_child(right)
            result = logic_node

        return result

    def parse_where_clause(self):
        """
        whereClause -> WHERE condition
        """
        self.parse('WHERE')
        condition = self.parse_condition()
        return WhereClause(condition)

    def parse_order_by_clause(self):
        """
        orderByClause -> ORDER BY IDENTIFIER
        """
        self.parse('ORDER')
        self.parse('BY')
        column = self.parse_identifier()
        return OrderByClause(column)

    def parse_select_statement(self) -> RootNode:
        """
        selectStatement -> SELECT selectList FROM tableName whereClause? orderByClause? ';'
        """
        root = RootNode()

        self.parse('SELECT')
        columns = self.parse_select_list()
        for col in columns:
            root.fields_node.add_column(col)

        self.parse('FROM')
        table = self.parse_table_name()
        root.tables_node.add_table(table)

        if self.is_parse('WHERE'):
            self.parse('WHERE')
            condition = self.parse_condition()
            root.add_where_clause(condition)

        order_by = None
        if self.is_parse('ORDER'):
            order_by = self.parse_order_by_clause()
            root.add_child(order_by)

        self.parse(';')

        # проверка на лишние символы
        if self.pos < len(self.text) and self.curr != '$':
            raise ParsingError(f'Лишний символ {self.curr} в позиции {self.pos}')

        return root

    def parse_query(self) -> RootNode:
        return self.parse_select_statement()