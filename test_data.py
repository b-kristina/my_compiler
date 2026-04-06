TEST_DATA = {
    'Users': [
        {'id': 1, 'name': 'Alice', 'age': 25, 'status': 'active'},
        {'id': 2, 'name': 'Bob', 'age': 17, 'status': 'inactive'},
        {'id': 3, 'name': 'Charlie', 'age': 30, 'status': 'active'},
        {'id': 4, 'name': 'Diana', 'age': 22, 'status': 'active'},
    ],
    'Products': [
        {'id': 1, 'name': 'Laptop', 'price': 999, 'category': 'electronics'},
        {'id': 2, 'name': 'Mouse', 'price': 25, 'category': 'electronics'},
        {'id': 3, 'name': 'Desk', 'price': 150, 'category': 'furniture'},
        {'id': 4, 'name': 'Chair', 'price': 75, 'category': 'furniture'},
    ],
    'Orders': [
        {'id': 1, 'user_id': 1, 'product_id': 1, 'quantity': 1},
        {'id': 2, 'user_id': 3, 'product_id': 2, 'quantity': 2},
        {'id': 3, 'user_id': 1, 'product_id': 3, 'quantity': 1},
    ],
}

TABLE_SCHEMA = {
    'Users': {
        'id': 'integer',
        'name': 'string',
        'age': 'integer',
        'status': 'string',
    },
    'Products': {
        'id': 'integer',
        'name': 'string',
        'price': 'integer',
        'category': 'string',
    },
    'Orders': {
        'id': 'integer',
        'user_id': 'integer',
        'product_id': 'integer',
        'quantity': 'integer',
    },
}