import base64


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _convert_md_to_whatsapp(response: str) -> str:
    """Convert a markdown string to WhatsApp markdown."""
    return response.replace("**", "*").replace("__", "_")
