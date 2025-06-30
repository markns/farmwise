import base64

from pywa_async.types.others import Contact as PywaContact

from farmwise.schema import Contact


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _convert_md_to_whatsapp(response: str) -> str:
    """Convert a markdown string to WhatsApp markdown."""
    return response.replace("**", "*").replace("__", "_").strip()


import copy
from dataclasses import fields, is_dataclass


def asdict_with_exclusions(obj, excluded: set):
    """
    Recursively converts a dataclass object to a dict, excluding specified fields.
    """
    if not obj:
        return None

    if not is_dataclass(obj):
        # For non-dataclass objects that asdict would normally deepcopy.
        # This part of the logic handles nested non-dataclass objects correctly.
        return copy.deepcopy(obj)

    result = []
    for f in fields(obj):
        # --- This is the crucial part ---
        # Skip the field if its name is in our exclusion set.
        if f.name in excluded:
            continue
        # --------------------------------

        value = getattr(obj, f.name)

        # Recursively call this function to handle nested dataclasses, lists, dicts, etc.
        if is_dataclass(value):
            result.append((f.name, asdict_with_exclusions(value, excluded)))
        elif isinstance(value, (list, tuple)):
            result.append((f.name, type(value)(asdict_with_exclusions(v, excluded) for v in value)))
        elif isinstance(value, dict):
            result.append(
                (
                    f.name,
                    type(value)(
                        (asdict_with_exclusions(k, excluded), asdict_with_exclusions(v, excluded))
                        for k, v in value.items()
                    ),
                )
            )
        else:
            # For simple types, just append them. deepcopy for safety.
            result.append((f.name, copy.deepcopy(value)))

    return dict(result)


def _convert_to_pywa_contact(contact: Contact) -> PywaContact:
    """Convert our Contact model to pywa Contact type."""

    # Create name object
    name = PywaContact.Name(formatted_name=contact.name)

    # Create phone list if phone is provided
    phones = []
    if contact.phone:
        phones.append(PywaContact.Phone(phone=contact.phone, wa_id=contact.phone, type="MOBILE"))

    # Create email list if email is provided
    emails = []
    if contact.email:
        emails.append(PywaContact.Email(email=contact.email, type="WORK"))

    # Create organization list if organization is provided
    orgs = []
    if contact.organization:
        orgs.append(PywaContact.Org(company=contact.organization))

    return PywaContact(
        name=name,
        phones=phones,
        emails=emails,
        # orgs=orgs,
    )
