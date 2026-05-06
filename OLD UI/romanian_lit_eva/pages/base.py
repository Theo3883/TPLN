from __future__ import annotations

from abc import ABC, abstractmethod


class Page(ABC):
    @abstractmethod
    def render(self) -> None:
        raise NotImplementedError
