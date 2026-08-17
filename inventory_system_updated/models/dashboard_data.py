from decimal import Decimal

from models.inventory_data import fetch_products
from models.report_data import fetch_report_transactions


def get_dashboard_summary(userID):
    products = fetch_products(userID)
    transactions = fetch_report_transactions(userID, active_products_only=True)
    total_products = len(products)
    total_stock = sum(int(product['stock'] or 0) for product in products)
    low_stock = sum(1 for product in products if int(product['stock'] or 0) <= 5)
    category_names = {
        product['categoryName'] or 'Uncategorised'
        for product in products
    }
    sales_value = sum(
        Decimal(str(transaction.get('totalValue') or 0))
        for transaction in transactions
        if transaction['type'] == 'sell'
    )
    restock_value = sum(
        Decimal(str(transaction.get('totalValue') or 0))
        for transaction in transactions
        if transaction['type'] in ('purchase', 'restock')
    )
    inventory_cost_value = sum(
        Decimal(str(product.get('costPrice') or 0)) * int(product['stock'] or 0)
        for product in products
    )
    inventory_sale_value = sum(
        Decimal(str(product.get('salePrice') or 0)) * int(product['stock'] or 0)
        for product in products
    )

    movement_types = [
        {'label': 'Sales', 'type': 'sell', 'count': 0, 'color': 'var(--red)'},
        {'label': 'Restocks', 'type': 'restock', 'count': 0, 'color': 'var(--orange)'},
        {'label': 'Purchases', 'type': 'purchase', 'count': 0, 'color': 'var(--accent)'},
        {'label': 'Deletes', 'type': 'delete', 'count': 0, 'color': '#8f2d56'},
    ]

    for movement in movement_types:
        movement['count'] = sum(
            1 for transaction in transactions if transaction['type'] == movement['type']
        )

    max_movement_count = max([movement['count'] for movement in movement_types] + [1])
    for movement in movement_types:
        movement['width'] = round((movement['count'] / max_movement_count) * 100, 1)

    category_stock = {}
    for product in products:
        category = product['categoryName'] or 'Uncategorised'
        category_stock[category] = category_stock.get(category, 0) + int(product['stock'] or 0)

    max_category_stock = max(category_stock.values(), default=1)
    category_chart = [
        {
            'label': category,
            'stock': stock,
            'width': round((stock / max_category_stock) * 100, 1) if max_category_stock else 0
        }
        for category, stock in sorted(category_stock.items())
    ]

    return {
        'products': products,
        'total_products': total_products,
        'total_stock': total_stock,
        'low_stock': low_stock,
        'total_categories': len(category_names),
        'sales_value': sales_value,
        'restock_value': restock_value,
        'net_value': sales_value - restock_value,
        'inventory_cost_value': inventory_cost_value,
        'inventory_sale_value': inventory_sale_value,
        'potential_margin': inventory_sale_value - inventory_cost_value,
        'movement_count': len(transactions),
        'movement_types': movement_types,
        'category_chart': category_chart
    }
