from query_executor import QueryExecutor
from code_generator import PythonCodeGenerator
from semantic_analyzer import SemanticAnalyzer
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
        "SELECT COUNT(*) FROM Users;",
        "SELECT SUM(age) FROM Users;",
        "SELECT AVG(age) FROM Users;",
        "SELECT MIN(age), MAX(age) FROM Users;",
        "SELECT COUNT(*) FROM Users WHERE age > 18;",
        "SELECT status, COUNT(*) FROM Users GROUP BY status;",
        "SELECT category, AVG(price) FROM Products GROUP BY category;",
        "SELECT * FROM NonExistentTable;",
        "SELECT invalid_col FROM Users;",
        "SELECT FROM Users;",
    ]

    analyzer = SemanticAnalyzer()
    executor = QueryExecutor()
    generator = PythonCodeGenerator()

    for i, sql in enumerate(test_queries, 1):
        print(f"\n{'=' * 60}")
        print(f"Тест {i}: {sql}")
        print('=' * 60)

        print("\n[1] Синтаксический анализ:")
        ast = parse_sql(sql)

        if not ast:
            print("    AST не построено")
            continue

        print("    Успешно")
        print("\n    AST Дерево:")
        TreePrinter.print_tree(ast, prefix="    ")

        print("\n[2] Семантический анализ:")
        if analyzer.analyze(ast):
            print("    Ошибок нет")
        else:
            print("    Найдены ошибки:")
            for error in analyzer.get_errors():
                print(f"    - {error}")
            continue

        print("\n[3] Генерация исполняемого кода:")
        generated_source = generator.generate(ast)
        for line in generated_source.rstrip().splitlines():
            print(f"    {line}")

        print("\n[4] Выполнение сгенерированного кода:")
        results = generator.execute(ast, executor.data)

        if results:
            columns = list(results[0].keys())

            widths = {col: len(col) for col in columns}
            for row in results:
                for col in columns:
                    widths[col] = max(widths[col], len(str(row[col])))

            header = " | ".join(col.ljust(widths[col]) for col in columns)
            print(f"    {header}")
            print(f"    {'-' * len(header)}")

            for row in results:
                line = " | ".join(str(row[col]).ljust(widths[col]) for col in columns)
                print(f"    {line}")

            print(f"\n    Всего строк: {len(results)}")
        else:
            print("    Пустой результат")


if __name__ == '__main__':
    main()