from farmbase_agent_toolkit.configuration import Context
from farmbase_client import APIConfig
from farmbase_client.models import Animal, SexEnum
from farmbase_client.services.animals_service import animals_create_animal

api_config = APIConfig(base_path = "http://127.0.0.1:8000")

def create_animal(context: Context, **kwargs):
    """
    Create a customer.

    Parameters:
        name (str): The name of the customer.
        email (str, optional): The email address of the customer.

    Returns:
        stripe.Customer: The created customer.
    """

    my_data = animals_create_animal(Animal(**kwargs), api_config_override=api_config)

    return my_data

if __name__ == '__main__':
    context = Context()
    r = create_animal(context, nickname=["Bessie"], animal_type="cow", sex=SexEnum.F)
    print(r)