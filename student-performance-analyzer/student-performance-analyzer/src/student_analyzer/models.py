"""The Student model: one person plus the marks they scored."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Optional


@dataclass
class Student:
    """A student and their marks, e.g. Student("Asha", {"Math": 88.0, "English": 74.5})."""

    name: str
    scores: dict[str, float] = field(default_factory=dict)

    @property
    def average(self) -> float:
        # A student with no marks at all gets 0.0 instead of crashing mean().
        if not self.scores:
            return 0.0
        return mean(self.scores.values())

    @property
    def best_subject(self) -> Optional[str]:
        if not self.scores:
            return None
        # If two subjects tie, max() keeps the first one it saw, so results stay predictable.
        return max(self.scores, key=self.scores.get)

    @property
    def weakest_subject(self) -> Optional[str]:
        if not self.scores:
            return None
        return min(self.scores, key=self.scores.get)
