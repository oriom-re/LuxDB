# 🔧 LuxDataMigration Toolkit

from sqlalchemy.orm import Session
from collections import Counter
import sqlalchemy as sa
import json

# ✅ 1. Analiza najczęściej używanych kluczy w `data`
def analyze_data_fields(session: Session, model_class, limit: int = 1000):
    """Zlicza najczęściej używane klucze w JSON-owym polu `data`"""
    rows = session.query(model_class.data).limit(limit).all()
    counter = Counter()

    for (row,) in rows:
        if isinstance(row, dict):
            counter.update(row.keys())

    return counter.most_common()


# 🔄 2. Migruj konkretne pole z `data` do nowej kolumny
def migrate_field_from_data(session: Session, model_class, field_name: str):
    """Przenosi wartość z `data[field_name]` do `model.field_name`"""
    items = session.query(model_class).all()
    for item in items:
        value = item.get_data(field_name)
        if value is not None:
            setattr(item, field_name, value)
    session.commit()


# 🔄 3. (Odwrotnie) z kolumny do `data`
def migrate_field_to_data(session: Session, model_class, field_name: str):
    """Przenosi wartość z `model.field_name` do `data[field_name]`"""
    items = session.query(model_class).all()
    for item in items:
        value = getattr(item, field_name, None)
        if value is not None:
            item.set_data(field_name, value)
    session.commit()


# 🧱 4. Przykładowy model z shadow-column
def add_shadow_column(model_class, name, column_type):
    """Przykładowy sposób ręcznego dodania kolumny z dostępem do `data`"""
    setattr(model_class, name, sa.orm.column_property(
        model_class.data[name].astext
    ))
    return model_class


# 🛠️ 5. Szablon migracji Alembic do ręcznego wklejenia
ALEMBIC_TEMPLATE = """
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('{table_name}', sa.Column('{field_name}', sa.{column_type}(), nullable=True))

def downgrade():
    op.drop_column('{table_name}', '{field_name}')
"""

def generate_alembic_stub(table_name: str, field_name: str, column_type: str = "String"):
    return ALEMBIC_TEMPLATE.format(
        table_name=table_name,
        field_name=field_name,
        column_type=column_type
    )


# 📦 Gotowe do użycia:
# print(analyze_data_fields(session, LuxSafeProfile))
# print(generate_alembic_stub("luxsafe_profiles", "soul_name"))
# migrate_field_from_data(session, LuxSafeProfile, "soul_name")
# migrate_field_to_data(session, LuxSafeProfile, "soul_name")
