from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from common.database.mysql import MySQL


@pytest.fixture
def mock_engine() -> MagicMock:
    return MagicMock(spec=Engine)


@pytest.fixture
def mock_session() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture
def mock_sessionmaker(mock_session) -> MagicMock:
    return MagicMock(return_value=mock_session)


@pytest.fixture
def mock_create_engine(mock_engine) -> Generator[MagicMock, MagicMock, None]:
    with patch("common.database.mysql.create_engine", return_value=mock_engine) as mock:
        yield mock


@pytest.fixture
def mock_scoped_session(mock_sessionmaker) -> Generator[MagicMock, MagicMock, None]:
    with patch("common.database.mysql.scoped_session", return_value=mock_sessionmaker) as mock:
        yield mock


def test_mysql_initialization(mock_create_engine, mock_scoped_session):
    db_user = "user"
    db_password = "password"
    db_host = "localhost"
    db_name = "test_db"
    db_port = 3306

    MySQL(db_user, db_password, db_host, db_name, db_port)

    expected_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4&collation=utf8mb4_general_ci"

    mock_create_engine.assert_called_once_with(expected_url, echo=False, pool_recycle=60)
    mock_scoped_session.assert_called_once()


def test_mysql_enter_exit(mock_create_engine, mock_scoped_session, mock_session):
    db_user = "user"
    db_password = "password"
    db_host = "localhost"
    db_name = "test_db"
    db_port = 3306

    mysql = MySQL(db_user, db_password, db_host, db_name, db_port)

    with mysql as session:
        assert session == mock_session

    mock_session.close.assert_called_once()


def test_mysql_commit(mock_create_engine, mock_scoped_session, mock_session):
    db_user = "user"
    db_password = "password"
    db_host = "localhost"
    db_name = "test_db"
    db_port = 3306

    mysql = MySQL(db_user, db_password, db_host, db_name, db_port)

    mysql.commit()
    mock_session.commit.assert_called_once()
