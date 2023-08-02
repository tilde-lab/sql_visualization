db_name = 'ooo_rubin'
tables = {'User': ['id', 'user_name'],
          'Personal_data': ['id', 'login', 'password', 'date_of_b', 'phone_number', 'telegram'],
          'History_of_shopping': ['user_id', 'transaction_id', 'total_price', 'payment_type'],
          'Movement_of_goods': ['transaction_id', 'product_id', 'date', 'time'],
          'Goods': ['product_id', 'name', 'price'],
          }

communication = {
    'User': [
        {'Personal_data': ['id', 'id']},
        {'History_of_shopping': ['id', 'user_id']}
    ],
    'Movement_of_goods': [
        {'Goods': ['product_id', 'product_id']},
        {'History_of_shopping': ['transaction_id', 'transaction_id']}
    ]
}