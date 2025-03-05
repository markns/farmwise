from farmbase_client.models import Animal

CREATE_ANIMAL_PROMPT = f"""
This tool creates an animal asset in Farmwise

It has the following arguments:
    animal_type: str = Field(..., description="Species/breed of the animal. Required field.")
    birthdate: Optional[datetime] = Field(None, description="Birthdate provided as a Unix timestamp or ISO date string.")
    is_castrated: Optional[bool] = Field(False, description="Indicates if the animal has been castrated.")
    nickname: List[str] = Field(description="List of nicknames for the animal.") # todo:, default_factory=list)
    sex: SexEnum = Field(..., description="Sex of the animal: 'F' for Female or 'M' for Male.")
"""
# https://github.com/langroid/langroid/blob/main/langroid/utils/pydantic_utils.py#L48

#
# CREATE_CUSTOMER_PROMPT = """
# This tool will create a customer in Stripe.
#
# It takes two arguments:
# - name (str): The name of the customer.
# - email (str, optional): The email of the customer.
# """
#
# LIST_CUSTOMERS_PROMPT = """
# This tool will fetch a list of Customers from Stripe.
#
# It takes no input.
# """
#
# CREATE_PRODUCT_PROMPT = """
# This tool will create a product in Stripe.
#
# It takes two arguments:
# - name (str): The name of the product.
# - description (str, optional): The description of the product.
# """
#
# LIST_PRODUCTS_PROMPT = """
# This tool will fetch a list of Products from Stripe.
#
# It takes one optional argument:
# - limit (int, optional): The number of products to return.
# """
#
# CREATE_PRICE_PROMPT = """
# This tool will create a price in Stripe. If a product has not already been
# specified, a product should be created first.
#
# It takes three arguments:
# - product (str): The ID of the product to create the price for.
# - unit_amount (int): The unit amount of the price in cents.
# - currency (str): The currency of the price.
# """
#
# LIST_PRICES_PROMPT = """
# This tool will fetch a list of Prices from Stripe.
#
# It takes two arguments:
# - product (str, optional): The ID of the product to list prices for.
# - limit (int, optional): The number of prices to return.
# """
#
# CREATE_PAYMENT_LINK_PROMPT = """
# This tool will create a payment link in Stripe.
#
# It takes two arguments:
# - price (str): The ID of the price to create the payment link for.
# - quantity (int): The quantity of the product to include in the payment link.
# """
#
# CREATE_INVOICE_PROMPT = """
# This tool will create an invoice in Stripe.
#
# It takes one argument:
# - customer (str): The ID of the customer to create the invoice for.
# """
#
# CREATE_INVOICE_ITEM_PROMPT = """
# This tool will create an invoice item in Stripe.
#
# It takes two arguments:
# - customer (str): The ID of the customer to create the invoice item for.
# - price (str): The ID of the price to create the invoice item for.
# """
#
# FINALIZE_INVOICE_PROMPT = """
# This tool will finalize an invoice in Stripe.
#
# It takes one argument:
# - invoice (str): The ID of the invoice to finalize.
# """
#
# RETRIEVE_BALANCE_PROMPT = """
# This tool will retrieve the balance from Stripe. It takes no input.
# """
#
# CREATE_REFUND_PROMPT = """
# This tool will refund a payment intent in Stripe.
#
# It takes three arguments:
# - payment_intent (str): The ID of the payment intent to refund.
# - amount (int, optional): The amount to refund in cents.
# - reason (str, optional): The reason for the refund.
# """
