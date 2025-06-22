from enum import Enum


class PostApiV1QuotesProductTypeProductType(str, Enum):
    EDUCATIONAL_ENDOWMENT_INSURANCE = "educational_endowment_insurance"
    PERSONAL_PENSION_INSURANCE = "personal_pension_insurance"

    def __str__(self) -> str:
        return str(self.value)
