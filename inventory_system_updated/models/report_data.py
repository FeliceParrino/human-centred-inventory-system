from database import get_connection
from models.schema import ensure_category_schema


def fetch_report_transactions(userID, start_date='', end_date='', active_products_only=False):
    ensure_category_schema()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = '''
        SELECT t.transactionID, t.type, t.timestamp, t.amount, t.totalValue, p.name, p.userID, u.username, c.name AS categoryName
        FROM transaction t
        JOIN product p ON t.productID = p.productID
        JOIN user u ON p.userID = u.userID
        LEFT JOIN category c ON p.categoryID = c.categoryID
        WHERE p.userID = %s
    '''
    params = [userID]

    if active_products_only:
        query += '''
            AND p.productID NOT IN (
                SELECT productID FROM transaction WHERE type = 'delete'
            )
        '''

    if start_date:
        query += ' AND DATE(t.timestamp) >= %s'
        params.append(start_date)

    if end_date:
        query += ' AND DATE(t.timestamp) <= %s'
        params.append(end_date)

    query += '''
        ORDER BY t.timestamp DESC
    '''

    cursor.execute(query, params)
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return transactions
