import unittest

from models.product import Product
from models.transaction import PurchaseTransaction, SellTransaction
from models.user import User


class TestProduct(unittest.TestCase):

    def test_purchase_product_increases_stock(self):
        product = Product(1, "Laptop", 10)
        product.purchase_product(5)
        self.assertEqual(product.get_stock(), 15)

    def test_sell_product_reduces_stock_when_available(self):
        product = Product(1, "Laptop", 10)
        result = product.sell_product(4)
        self.assertTrue(result)
        self.assertEqual(product.get_stock(), 6)

    def test_sell_product_fails_when_stock_is_insufficient(self):
        product = Product(1, "Laptop", 3)
        result = product.sell_product(5)
        self.assertFalse(result)
        self.assertEqual(product.get_stock(), 3)


class TestUser(unittest.TestCase):

    def test_hash_password_returns_a_different_value(self):
        plain_password = "MyPassword123!"
        hashed_password = User.hash_password(plain_password)
        self.assertNotEqual(plain_password, hashed_password)

    def test_verify_password_returns_true_for_matching_password(self):
        hashed_password = User.hash_password("MyPassword123!")
        user = User(1, "felix", hashed_password)
        self.assertTrue(user.verify_password("MyPassword123!"))

    def test_verify_password_returns_false_for_wrong_password(self):
        hashed_password = User.hash_password("MyPassword123!")
        user = User(1, "felix", hashed_password)
        self.assertFalse(user.verify_password("WrongPassword"))


class TestTransaction(unittest.TestCase):

    def test_purchase_transaction_execute_increases_stock(self):
        product = Product(1, "Laptop", 10)
        transaction = PurchaseTransaction(1, product, 5)
        result = transaction.execute()
        self.assertEqual(result, "Purchase successful.")
        self.assertEqual(product.get_stock(), 15)

    def test_sell_transaction_execute_reduces_stock(self):
        product = Product(1, "Laptop", 10)
        transaction = SellTransaction(1, product, 4)
        result = transaction.execute()
        self.assertEqual(result, "Sale successful.")
        self.assertEqual(product.get_stock(), 6)

    def test_sell_transaction_execute_returns_insufficient_stock(self):
        product = Product(1, "Laptop", 2)
        transaction = SellTransaction(1, product, 5)
        result = transaction.execute()
        self.assertEqual(result, "Insufficient stock.")
        self.assertEqual(product.get_stock(), 2)


if __name__ == '__main__':
    unittest.main()
