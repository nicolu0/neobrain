from abc import ABC, abstractmethod

class FactExtractor(ABC):
    """
    interface for fact extractors

    both rule-based and LLM-based extractors implement this
    """

    @abstractmethod
    def extract(self, text: str) -> list[str]:
        """
        extracts atomic facts from raw user chat input

        args:
            text: raw user input ("I just moved to California")

        returns:
            list of strings, each element being a fact extracted from user input
        """
        ...
