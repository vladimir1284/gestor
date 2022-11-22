from inventory.models import Transaction, Order, Stock, Profit

sell_orders = Order.objects.filter(type='sell')

for order in sell_orders:
    sells = Transaction.objects.filter(order=order)
    for sell in sells:
        stock = Stock.objects.filter(product=sell.product)[0]
        gain = sell.quantity * \
            (sell.price*(1-sell.product.sell_tax/100)-stock.cost)
        profit = Profit.objects.create(product=sell.product,
                                       quantity=sell.quantity,
                                       created_date=order.created_date,
                                       profit=gain)
        profit.save()
