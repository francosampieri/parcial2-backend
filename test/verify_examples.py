"""Ejecuta los ejemplos .http sobre PostgreSQL privado, sin tocar .env."""
import asyncio
import json
import os
import re
from pathlib import Path

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from tests.pg_cluster import create_cluster


async def verify() -> None:
    cluster = create_cluster()
    try:
        os.environ["DATABASE_URL"] = cluster.url
        os.environ["SQL_ECHO"] = "false"
        from app.demo_seed import seed_examples
        from app.main import create_app

        app = create_app()
        async with LifespanManager(app):
            async with app.state.session_factory() as session:
                async with session.begin():
                    ids = await seed_examples(session)
            variables = {
                "base": "http://test", "editorial": ids["editorial"],
                "genero": ids["genero"], "autor1": ids["autores"][0],
                "autor2": ids["autores"][1], "libro25000": ids["libros"][0],
                "libro27000": ids["libros"][3], "libroDosAutores": ids["libros"][2],
                "cliente": ids["cliente"],
            }
            source = Path(__file__).with_name("C-01-a-C-08.http").read_text(encoding="utf-8")
            count = 0
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                for section in source.split("### ")[1:]:
                    lines = section.splitlines()
                    heading = lines[0]
                    request_line = next((line for line in lines if re.match(r"^(GET|POST|PATCH) ", line)), None)
                    if request_line is None:
                        continue
                    method, url = request_line.split(" ", 1)
                    url = re.sub(r"\{\{(\w+)\}\}", lambda match: str(variables[match.group(1)]), url)
                    body_line = next((line for line in lines if line.startswith("{")), None)
                    body = None
                    if body_line:
                        body_line = re.sub(r"\{\{(\w+)\}\}", lambda match: str(variables[match.group(1)]), body_line)
                        body = json.loads(body_line)
                    response = await client.request(method, url, json=body)
                    expected = re.search(r"— (\d{3})", heading)
                    if expected and response.status_code != int(expected.group(1)):
                        raise AssertionError(f"{heading}: esperado {expected.group(1)}, recibido {response.status_code}: {response.text}")
                    capture = re.search(r'client\.global\.set\("(\w+)", response\.body\.id\)', section)
                    if capture:
                        variables[capture.group(1)] = response.json()["id"]
                    count += 1
            assert len(re.findall(r"\[OP \d{2}\]", source)) == 26
            print(f"HTTP_EXAMPLES {count} peticiones verificadas, 26 operaciones, C-01 a C-08 OK")
    finally:
        cluster.cleanup()


if __name__ == "__main__":
    asyncio.run(verify())
