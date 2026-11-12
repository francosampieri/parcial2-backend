"""Evidencia integral C06/C07 sobre PostgreSQL privado."""
from decimal import Decimal

import pytest
from sqlalchemy import event, text


@pytest.mark.asyncio
async def test_sale_history_restart_and_fixed_detail_queries(application, database_url):
    from asgi_lifespan import LifespanManager
    from httpx import ASGITransport, AsyncClient
    from app.demo_seed import seed_examples
    from app.main import create_app

    async with application.state.session_factory() as session:
        async with session.begin():
            ids = await seed_examples(session)

    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as client:
        one = await client.post("/ventas/", json={
            "cliente_id": ids["cliente"],
            "renglones": [{"libro_id": ids["libros"][0], "cantidad": 1}],
        })
        assert one.status_code == 201, one.text
        two = await client.post("/ventas/", json={
            "cliente_id": ids["cliente"],
            "renglones": [
                {"libro_id": ids["libros"][0], "cantidad": 2},
                {"libro_id": ids["libros"][3], "cantidad": 1},
            ],
        })
        assert two.status_code == 201, two.text
        sale = two.json()
        assert Decimal(str(sale["total"])) == Decimal("77000.00")
        assert [Decimal(str(line["precio_unitario"])) for line in sale["renglones"]] == [Decimal("25000.00"), Decimal("27000.00")]
        changed = await client.patch(f'/libros/{ids["libros"][0]}', json={"precio": "30000.00"})
        assert changed.status_code == 200, changed.text
        assert Decimal(str((await client.get(f'/ventas/{sale["id"]}')).json()["total"])) == Decimal("77000.00")

    # Otra instancia de FastAPI sobre las mismas tablas: comprueba persistencia.
    restarted = create_app()
    async with LifespanManager(restarted):
        counts = {}

        def count_query(_conn, _cursor, statement, _parameters, _context, _executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                counts["current"] += 1

        event.listen(restarted.state.engine.sync_engine, "before_cursor_execute", count_query)
        try:
            async with AsyncClient(transport=ASGITransport(app=restarted), base_url="http://test") as client:
                async def measured(path):
                    counts["current"] = 0
                    response = await client.get(path)
                    assert response.status_code == 200, response.text
                    return response.json(), counts["current"]

                one_book, book_sql_one = await measured(f'/libros/{ids["libros"][0]}')
                multi_book, book_sql_multi = await measured(f'/libros/{ids["libros"][2]}')
                one_sale, sale_sql_one = await measured(f'/ventas/{one.json()["id"]}')
                multi_sale, sale_sql_multi = await measured(f'/ventas/{sale["id"]}')
                assert len(one_book["autores"]) == 1
                assert len(multi_book["autores"]) == 2
                assert len(one_sale["renglones"]) == 1
                assert len(multi_sale["renglones"]) == 2
                assert book_sql_one == book_sql_multi
                assert sale_sql_one == sale_sql_multi
                assert Decimal(str(multi_sale["total"])) == Decimal("77000.00")
                assert Decimal(str(multi_sale["renglones"][0]["precio_unitario"])) == Decimal("25000.00")
                print(f"C06_EVIDENCE book_selects={book_sql_one}/{book_sql_multi} sale_selects={sale_sql_one}/{sale_sql_multi} total={multi_sale['total']} historical_price={multi_sale['renglones'][0]['precio_unitario']}")
        finally:
            event.remove(restarted.state.engine.sync_engine, "before_cursor_execute", count_query)

    # La suite histórica usa IDs de ejemplo fijos: retirar sólo las filas de este caso.
    async with application.state.engine.begin() as connection:
        for statement, params in (
            ("DELETE FROM renglon_venta WHERE venta_id = ANY(:ids)", {"ids": [one.json()["id"], sale["id"]]}),
            ("DELETE FROM venta WHERE id = ANY(:ids)", {"ids": [one.json()["id"], sale["id"]]}),
            ("DELETE FROM libro_autor WHERE libro_id = ANY(:ids)", {"ids": ids["libros"]}),
            ("DELETE FROM libro WHERE id = ANY(:ids)", {"ids": ids["libros"]}),
            ("DELETE FROM autor WHERE id = ANY(:ids)", {"ids": ids["autores"]}),
            ("DELETE FROM cliente WHERE id = :id", {"id": ids["cliente"]}),
            ("DELETE FROM genero WHERE id = :id", {"id": ids["genero"]}),
            ("DELETE FROM editorial WHERE id = :id", {"id": ids["editorial"]}),
        ):
            await connection.execute(text(statement), params)
