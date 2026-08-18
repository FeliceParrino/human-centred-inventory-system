from database import get_connection
from models.schema import ensure_category_schema


def fetch_categories(userID):
    ensure_category_schema()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT categoryID, name FROM category WHERE userID = %s ORDER BY name',
        (userID,)
    )
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories


def fetch_products(userID):
    ensure_category_schema()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.productID, p.name, p.stock, p.costPrice, p.salePrice, p.categoryID, u.username, c.name AS categoryName
        FROM product p
        JOIN user u ON p.userID = u.userID
        LEFT JOIN category c ON p.categoryID = c.categoryID
        WHERE p.userID = %s
          AND p.productID NOT IN (
              SELECT productID FROM transaction WHERE type = 'delete'
          )
        ORDER BY c.name IS NULL, c.name, p.name
    ''', (userID,))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products


def fetch_active_product(productID, userID):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        '''
        SELECT * FROM product
        WHERE productID = %s
          AND userID = %s
          AND productID NOT IN (
              SELECT productID FROM transaction WHERE type = 'delete'
          )
        ''',
        (productID, userID)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_user_category_id(categoryID, userID):
    if categoryID is None:
        return None

    ensure_category_schema()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT categoryID FROM category WHERE categoryID = %s AND userID = %s',
        (categoryID, userID)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row['categoryID'] if row else None


def fetch_category(categoryID, userID):
    ensure_category_schema()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT categoryID, name FROM category WHERE categoryID = %s AND userID = %s',
        (categoryID, userID)
    )
    category = cursor.fetchone()
    cursor.close()
    conn.close()
    return category
