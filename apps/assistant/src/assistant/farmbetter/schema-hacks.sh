

replace _GqTimelineEntryInput > GqTimelineEntryInput
replace _GqTimelineEntryDto > GqTimelineEntryDto


class GqTimelineEntryInput(BaseModel):
    ..
    model_config = {
        "populate_by_name": True # allows for from_ in constructor
    }



class GqUserModelDto(BaseModel):
   ...
    # (Optional) be explicit about eq/hash semantics
    def __hash__(self) -> int:
        return hash(self.wa_id)

    def __eq__(self, other) -> bool:
        return isinstance(other, GqUserModelDto) and self.wa_id == other.wa_id

    @computed_field(return_type=Optional[str])
    def full_name(self) -> Optional[str]:
        return f"{self.firstName} {self.lastName}"

    @computed_field(return_type=Optional[str])
    def wa_id(self) -> Optional[str]:
        """WhatsApp ID: E.164 numeric without '+' = country_code + national number."""
        return f"{self.countryCode}{self.phoneNumber}"