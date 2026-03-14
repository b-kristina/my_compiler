from sql_parser import SqlParser
from parser_base import ParsingError


def main():
    # Тестовые запросы
    test_queries = [
        "SELECT * FROM Users;",
        "SELECT id, name FROM Users WHERE age > 18;",
        "SELECT name FROM Products WHERE price <= 100 ORDER BY name;",
        "SELECT id FROM Users WHERE age > 18 AND status = 'active';",
        "SELECT FROM Users;",  # для теста ошибки
    ]

    for sql in test_queries:
        print(f"\n{'=' * 50}")
        print(f"Запрос: {sql}")
        print('=' * 50)

        try:
            parser = SqlParser(sql)
            ast = parser.parse_query()
            print("\n AST Дерево:")
            ast.print_tree()
        except ParsingError as e:
            print(f"\n Синтаксическая ошибка: {e}")
        except Exception as e:
            print(f"\n Ошибка: {e}")


if __name__ == '__main__':
    main()