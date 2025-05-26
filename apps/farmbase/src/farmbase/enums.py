from enum import StrEnum


class FarmbaseEnum(StrEnum):
    """
    A custom Enum class that extends StrEnum.

    This class inherits all functionality from StrEnum, including
    string representation and automatic value conversion to strings.

    Example:
        class Visibility(DispatchEnum):
            OPEN = "Open"
            RESTRICTED = "Restricted"

        assert str(Visibility.OPEN) == "Open"

    Note:
        In `3.12` we will get `__contains__` functionality:

        DeprecationWarning: in 3.12 __contains__ will no longer raise TypeError, but will return True or
        False depending on whether the value is a member or the value of a member
    """

    pass  # No additional implementation needed


class Visibility(FarmbaseEnum):
    open = "Open"
    restricted = "Restricted"


class SearchTypes(FarmbaseEnum):
    definition = "Definition"
    document = "Document"
    incident = "Incident"
    incident_priority = "IncidentPriority"
    incident_type = "IncidentType"
    individual_contact = "IndividualContact"
    plugin = "Plugin"
    query = "Query"
    search_filter = "SearchFilter"
    case = "Case"
    service = "Service"
    source = "Source"
    tag = "Tag"
    task = "Task"
    team_contact = "TeamContact"
    term = "Term"


class UserRoles(FarmbaseEnum):
    owner = "Owner"
    manager = "Manager"
    admin = "Admin"
    member = "Member"


class DocumentResourceTypes(FarmbaseEnum):
    case = "dispatch-case-document"
    executive = "dispatch-executive-report-document"
    incident = "dispatch-incident-document"
    review = "dispatch-incident-review-document"
    tracking = "dispatch-incident-sheet"


class DocumentResourceReferenceTypes(FarmbaseEnum):
    conversation = "dispatch-conversation-reference-document"
    faq = "dispatch-incident-reference-faq-document"


class DocumentResourceTemplateTypes(FarmbaseEnum):
    case = "dispatch-case-document-template"
    executive = "dispatch-executive-report-document-template"
    incident = "dispatch-incident-document-template"
    review = "dispatch-incident-review-document-template"
    tracking = "dispatch-incident-tracking-template"
    forms = "dispatch-forms-export-template"


class EventType(FarmbaseEnum):
    other = "Other"  # default and catch-all (x resource created/updated, etc.)
    field_updated = "Field updated"  # for fields like title, description, tags, type, etc.
    assessment_updated = "Assessment updated"  # for priority, status, or severity changes
    participant_updated = "Participant updated"  # for added/removed users and role changes
    imported_message = "Imported message"  # for stopwatch-reacted messages from Slack
    custom_event = "Custom event"  # for user-added events (new feature)


class SubjectNames(FarmbaseEnum):
    CASE = "Case"
    INCIDENT = "Incident"
    SIGNAL = "Signal"


class ProductCategory(FarmbaseEnum):
    """Categories of agricultural products."""

    fungicide = "Fungicide"
    insecticide = "Insecticide"
    herbicide = "Herbicide"


class ContactRole(FarmbaseEnum):
    FARMER = "farmer"
    EXTENSION_OFFICER = "extension_officer"
    OTHER = "other"


class FarmContactRole(FarmbaseEnum):
    OWNER = "owner"
    FAMILY = "family"
    WORKER = "worker"
    ADVISOR = "advisor"


class Gender(FarmbaseEnum):
    MALE = "male"
    FEMALE = "female"
