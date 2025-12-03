from pywa.types.template_v2 import TemplateV2

# wa = WhatsApp(...)
#
# wa.create_template(
#     template=TemplateV2(
#         name='buy_new_iphone_x',
#         category=NewTemp.Category.MARKETING,
#         language=NewTemp.Language.ENGLISH_US,
#         header=NewTemp.Text('The New iPhone {15} is here!'),
#         body=NewTemp.Body('Buy now and use the code {WA_IPHONE_15} to get {15%} off!'),
#         footer=NewTemp.Footer('Powered by PyWa'),
#         buttons=[
#             NewTemp.UrlButton(title='Buy Now', url='https://example.com/shop/{iphone15}'),
#             NewTemp.PhoneNumberButton(title='Call Us', phone_number='1234567890'),
#             NewTemp.QuickReplyButton('Unsubscribe from marketing messages'),
#             NewTemp.QuickReplyButton('Unsubscribe from all messages'),
#         ],
#     ),
# )