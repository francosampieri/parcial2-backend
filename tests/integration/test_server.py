"""Verificación final del servidor real y de los comandos del README."""
import asyncio
import socket

from httpx import AsyncClient
import pytest
from sqlalchemy import event
import uvicorn


@pytest.mark.asyncio
async def test_uvicorn_objeto_documentado_http_real_y_apagado(database_url, monkeypatch):
    from app import main
    disposed = []
    original = main.create_async_engine
    def tracked_engine(*args, **kwargs):
        engine = original(*args, **kwargs)
        event.listen(engine.sync_engine, "engine_disposed", lambda _: disposed.append(engine))
        return engine
    monkeypatch.setattr(main, "create_async_engine", tracked_engine)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config("app.main:app", host="127.0.0.1", port=port, loop="asyncio", http="h11", lifespan="on", log_level="warning"))
    task = asyncio.create_task(server.serve(sockets=[listener]))
    try:
        async with asyncio.timeout(10):
            while not server.started:
                if task.done():
                    await task
                    pytest.fail("Uvicorn terminó antes de servir")
                await asyncio.sleep(0.02)
        async with AsyncClient(base_url=f"http://127.0.0.1:{port}") as client:
            assert (await client.get("/health/live")).json() == {"estado": "vivo"}
            assert (await client.get("/health/ready")).json() == {"estado": "listo"}
            assert (await client.get("/docs")).status_code == 200
    finally:
        server.should_exit = True
        await asyncio.wait_for(task, timeout=10)
        listener.close()
    assert len(disposed) == 1
    assert disposed[0] is main.app.state.engine
