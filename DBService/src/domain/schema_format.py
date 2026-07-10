from __future__ import annotations

from src.domain.models import DatabaseSchema


def schema_to_dict(schema: DatabaseSchema) -> dict:
    return {
        "tables": [
            {
                "name": table.name,
                "columns": [
                    {
                        "name": col.name,
                        "type": col.type,
                        "nullable": col.nullable,
                        "primary_key": col.primary_key,
                    }
                    for col in table.columns
                ],
            }
            for table in schema.tables
        ]
    }


def format_schema_text(schema: DatabaseSchema) -> str:
    lines: list[str] = []
    for table in schema.tables:
        lines.append(f'Table "{table.name}":')
        for col in table.columns:
            parts = [col.type]
            if col.primary_key:
                parts.append("PRIMARY KEY")
            parts.append("NULL" if col.nullable else "NOT NULL")
            lines.append(f"  - {col.name}: {' '.join(parts)}")
        lines.append("")
    return "\n".join(lines).strip()
