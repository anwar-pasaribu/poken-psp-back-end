def get_shopping_cart_item_fee(sc):
    total_cost = 0
    if sc.product.is_discount:
        sc.product.price = (sc.product.price - ((sc.product.price * sc.product.discount_amount) / 100))
    total_cost += sc.product.price * sc.quantity + sc.shipping_fee

    return total_cost

def get_discounted_product_fee(product):
    return (product.price - ((product.price * product.discount_amount) / 100))