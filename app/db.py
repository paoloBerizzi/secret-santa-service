from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine


def make_engine(url: str) -> Engine:
    engine = create_engine(url, pool_pre_ping=True, hide_parameters=True)
    if engine.dialect.name == 'sqlite':
        event.listen(engine, 'connect', enable_foreign_keys)
    return engine


def enable_foreign_keys(connection, _record) -> None:
    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()