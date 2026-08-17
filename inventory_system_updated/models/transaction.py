from abc import ABC, abstractmethod
from datetime import datetime

class Transaction(ABC):

    def __init__(self, transactionID, product, quantity=0):
        self.transactionID = transactionID
        self.product = product
        self._quantity = quantity
        self._timestamp = datetime.now()

        
    @abstractmethod
    def execute(self):
        pass


class PurchaseTransaction(Transaction):
    def execute(self):
           self.product.purchase_product(self._quantity)     
           return "Purchase successful."


class SellTransaction(Transaction):
    def execute(self):
        if self.product.sell_product(self._quantity):
            return "Sale successful."
        return "Insufficient stock."
