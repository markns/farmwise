# from farmbase_agent_toolkit.configuration import Context
# from farmbase_client import APIConfig
# from farmbase_client.models import Animal, SexEnum
# from farmbase_client.services.animals_service import animals_create_animal
#
from farmbase_client import AuthenticatedClient as FarmbaseClient
from farmbase_client.api.farms import farms_create_farm
from farmbase_client.api.fields import fields_create_field
from farmbase_client.models import FarmCreate, FieldCreate

# api_config = APIConfig(base_path = "http://127.0.0.1:8000")
#
# def create_animal(context: Context, **kwargs):
#
#     my_data = animals_create_animal(Animal(**kwargs), api_config_override=api_config)
#
#     return my_data
#
# if __name__ == '__main__':
#     context = Context()
#     r = create_animal(context, nickname=["Bessie"], animal_type="cow", sex=SexEnum.F)
#     print(r)
from uuid import UUID

from farmbase_client.api.fields import fields_create_field
from farmbase_client.models import FieldCreate


def create_field(farm_id: UUID, field: FieldCreate):
    pass
    # with FarmbaseClient(base_url=self.url, token=self._secret_key) as client:
    #     response = fields_create_field.sync(client=client,
    #                                         body=FieldCreate(**kwargs))
    #
    #     return response.model_dump_json()