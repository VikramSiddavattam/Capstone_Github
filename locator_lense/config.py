"""MVP configuration and fixed business rules."""

from dataclasses import dataclass


LOCATOR_SCORES = {
    "id": 100,
    "name": 90,
    "data-testid": 85,
    "CSS Selector": 75,
    "XPath": 65,
}
LOCATOR_PRIORITY = ("id", "name", "data-testid", "XPath", "CSS Selector")


@dataclass(frozen=True)
class Settings:
    redirect_limit: int = 10
    connect_timeout_seconds: float = 5.0
    read_timeout_seconds: float = 10.0

    @property
    def request_timeout(self) -> tuple[float, float]:
        return (self.connect_timeout_seconds, self.read_timeout_seconds)
