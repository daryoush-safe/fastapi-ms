import httpx

from DBService.src.domain.ports.sql_generator import ISQLGenerator


class PrunerSQLGenerator(ISQLGenerator):
    def __init__(self, base_url: str, client: httpx.AsyncClient) -> None:
        self._base_url = base_url
        self._client = client

    async def generate(self, schema: dict, prompt: str) -> str:
        response = await self._client.post(
            f"{self._base_url}/generate",
            json={"schema": schema, "prompt": prompt},
        )
        response.raise_for_status()
        
        return response.json()["sql"]
