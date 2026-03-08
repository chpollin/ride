from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QuestionnaireItem:
    id: str
    label: str
    description: str = ""
    catalogue_ref: str = ""
    value: Optional[bool] = None  # True=Yes, False=No, None=N/A
    value_label: str = ""  # "Yes", "No", "Not applicable", or specific option text
    children: list["QuestionnaireItem"] = field(default_factory=list)
    gloss: str = ""  # Free-text for "Other" options

    @property
    def is_section(self) -> bool:
        return not self.id and len(self.children) > 0


@dataclass
class QuestionnaireSection:
    name: str
    items: list[QuestionnaireItem] = field(default_factory=list)

    @property
    def total_yes(self) -> int:
        return sum(1 for item in self._flat_items() if item.value is True)

    @property
    def total_no(self) -> int:
        return sum(1 for item in self._flat_items() if item.value is False)

    @property
    def total_na(self) -> int:
        return sum(1 for item in self._flat_items() if item.value is None)

    def _flat_items(self) -> list[QuestionnaireItem]:
        result = []
        for item in self.items:
            if item.children:
                result.extend(item.children)
            else:
                result.append(item)
        return result


@dataclass
class Questionnaire:
    schema_type: str  # "se", "dtc", "te"
    schema_url: str = ""
    resource_id: str = ""  # For tools: "rev1", "rev2", etc.
    resource_label: str = ""  # For tools: name of the reviewed tool
    sections: list[QuestionnaireSection] = field(default_factory=list)

    @property
    def total_yes(self) -> int:
        return sum(s.total_yes for s in self.sections)

    @property
    def total_no(self) -> int:
        return sum(s.total_no for s in self.sections)

    @property
    def total_na(self) -> int:
        return sum(s.total_na for s in self.sections)

    @property
    def total_answered(self) -> int:
        return self.total_yes + self.total_no

    @property
    def score_percentage(self) -> float:
        total = self.total_answered
        if total == 0:
            return 0.0
        return (self.total_yes / total) * 100
