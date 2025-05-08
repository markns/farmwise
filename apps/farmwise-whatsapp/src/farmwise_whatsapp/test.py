import os

from pywa import WhatsApp
from pywa.types import Template

wa = WhatsApp(
    phone_id=os.environ.get("WHATSAPP_PHONE_ID"),  # The phone id you got from the API Setup
    token=os.environ.get("WHATSAPP_TOKEN"),  # The token you got from the API Setup
)

TO_NUMBER = "+254748256530"

# wa.send_template(to=TO_NUMBER,
#                  template=Template(name='hello_world', language=Template.Language.ENGLISH_US))

# wa.send_message(
#     to='+254748256530',
#     text='Hi! This message sent from pywa!'
# )

# wa.send_image(
#     to='+254748256530',
#     image='https://www.rd.com/wp-content/uploads/2021/04/GettyImages-1053735888-scaled.jpg'
# )
#

wa.request_location(
    to=TO_NUMBER,
    text="Please share your location with us.",
)

wa.send_location(
    to=TO_NUMBER,
    latitude=37.4847483695049,
    longitude=-122.1473373086664,
    name="WhatsApp HQ",
    address="Menlo Park, 1601 Willow Rd, United States",
)
