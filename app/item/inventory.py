from app.item.item import Item


class Inventory:
    MAX_CAPACITY = 48
    MAX_MONEY = 99_999

    def __init__(self, capacity=MAX_CAPACITY):
        self.capacity = capacity
        self.money = 0
        self.items: list[Item] = []

    def add_item(self, item: Item):
        if len(self.items) < self.capacity:
            self.items.append(item)

    def add_money(self, amount: int):
        self.money = min(amount + self.money, Inventory.MAX_MONEY)
