from sqladmin import ModelView
from models.product import Product


class ProductAdmin(ModelView, model=Product):
    """Admin view configuration for the Product model."""
    column_list = [Product.id, Product.name, Product.price, Product.stock]
    column_searchable_list = [Product.name]
    can_create = True
    can_delete = True


