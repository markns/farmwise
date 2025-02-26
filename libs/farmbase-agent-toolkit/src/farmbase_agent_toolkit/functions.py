import farmstore_client
from agent_toolkit.configuration import Context
from farmstore.assets import SexEnum
from farmstore_client.api.animals import animals_create_animal
from farmstore_client.models import Animal


def create_animal(context: Context, **kwargs):
    """
    Create a customer.

    Parameters:
        name (str): The name of the customer.
        email (str, optional): The email address of the customer.

    Returns:
        stripe.Customer: The created customer.
    """

    client = farmstore_client.Client(base_url="http://localhost:8000")

    with client as client:
        my_data = animals_create_animal.sync(client=client, body=Animal(**kwargs))
        # or if you need more info (e.g. status_code)
        # response: Response[MyDataModel] = get_my_data_model.sync_detailed(client=client)

    return my_data

if __name__ == '__main__':
    context = Context()
    r = create_animal(context, nickname=["Bessie"], animal_type="cow", sex=SexEnum.F)
    print(r)