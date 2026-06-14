from abc import ABC, abstractmethod

class ISQLGenerator(ABC):
    @abstractmethod
    async def generate(self, schema: dict, prompt: str) -> str: ...