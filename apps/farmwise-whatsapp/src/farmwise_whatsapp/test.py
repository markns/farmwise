import os

from pywa import WhatsApp
from pywa.types import Template

wa = WhatsApp(
    phone_id=os.environ.get('WHATSAPP_PHONE_ID'),  # The phone id you got from the API Setup
    token=os.environ.get('WHATSAPP_TOKEN')  # The token you got from the API Setup
)

wa.send_template(to='+254748256530',
                 template=Template(name='hello_world', language=Template.Language.ENGLISH_US))

# wa.send_message(
#     to='+254748256530',
#     text='Hi! This message sent from pywa!'
# )

wa.send_image(
    to='+254748256530',
    image='https://www.rd.com/wp-content/uploads/2021/04/GettyImages-1053735888-scaled.jpg'
)