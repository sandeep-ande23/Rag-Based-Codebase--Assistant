from .database import get_engine

def get_order(order_id: int):
    engine = get_engine()
    with engine.connect() as connection:
        result = connection.execute(
            "SELECT * FROM orders WHERE id = :id",
            {"id": order_id},
        )
        return result.fetchone()
