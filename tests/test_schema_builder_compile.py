from typing import Any, Dict

from core.gbt.engine.ddl.schema_builder import SchemaBuilderEngine


def _build_manifest() -> Dict[str, Any]:
    return {
        "customer": {
            "version": 1.0,
            "models": {
                "type": "node",
                "label": "customer",
                "properties": [
                    {
                        "name": "gid",
                        "data_type": "string",
                        "constraints": ["IS UNIQUE"],
                        "indexes": ["index"],
                    },
                    {
                        "name": "district",
                        "data_type": "string",
                        "indexes": ["fulltext"],
                    },
                ],
            },
        }
    }


def test_compile_generates_constraints_and_indexes(monkeypatch) -> None:
    writes = []

    def fake_manifest(self):
        return _build_manifest()

    def fake_write_compile_cypher(**kwargs):
        writes.append(kwargs)

    monkeypatch.setattr(SchemaBuilderEngine, "_load_manifest", fake_manifest)
    monkeypatch.setattr(
        "core.gbt.engine.ddl.schema_builder.write_compile_cypher",
        fake_write_compile_cypher,
    )

    engine = SchemaBuilderEngine(model_name="customer")
    statements = engine.compile()

    assert len(statements) == 3
    assert any("CREATE CONSTRAINT" in stmt for stmt in statements)
    assert any("CREATE INDEX" in stmt for stmt in statements)
    assert any("CREATE FULLTEXT INDEX" in stmt for stmt in statements)

    written_names = {item["compile_model_name"] for item in writes}
    assert "customer_gid_is_unique_constraint" in written_names
    assert "customer_gid_index" in written_names
    assert "customer_district_fulltext_index" in written_names
