from sql_parser import SqlParser
from parser_base import ParsingError
from tree_printer import TreePrinter


def parse_sql(sql_input: str):
    """Парсинг SQL-запроса"""
    try:
        parser = SqlParser(sql_input)
        ast = parser.parse_query()
        return ast
    except ParsingError as e:
        print(f"\n СИНТАКСИЧЕСКАЯ ОШИБКА (позиция {parser.pos if 'parser' in locals() else 0}):")
        print(f"   {e}")
        return None
    except Exception as e:
        print(f"\n ОШИБКА: {e}")
        return None


def main():
    test_queries = [
        "SELECT * FROM Users;",
        "SELECT id, name FROM Users WHERE age > 18;",
        "SELECT name FROM Products WHERE price <= 100 ORDER BY name;",
        "SELECT id FROM Users WHERE age > 18 AND status = 'active';",
        "SELECT FROM Users;",  # ошибка
    ]

    for i, sql in enumerate(test_queries, 1):
        print(f"\n{'=' * 60}")
        print(f"Тест {i}: {sql}")
        print('=' * 60)

        ast = parse_sql(sql)

        if ast:
            print("\n AST Дерево:")
            TreePrinter.print_tree(ast)
        else:
            print("\n AST не построено из-за синтаксических ошибок.")

if __name__ == '__main__':
    main()
