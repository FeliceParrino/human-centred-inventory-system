class Product:
    def __init__(self, productID, name, stock=0):
        self.productID = productID
        self.name = name
        self.__stock = int(stock)

    def get_stock(self):
        return self.__stock
    
    def purchase_product(self, amount):
        self.__stock += amount

    def sell_product(self, amount):
        if amount <= self.__stock:
            self.__stock -= amount
            return True
        return False
        
