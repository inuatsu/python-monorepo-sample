from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session


class MySQL:
    def __init__(self, db_user: str, db_password: str, db_host: str, db_name: str, db_port: int = 3306) -> None:
        self.database_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4&collation=utf8mb4_general_ci"
        self.engine = create_engine(self.database_url, echo=False, pool_recycle=60)
        self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))()

    def __enter__(self) -> Session:
        return self.session

    def commit(self) -> None:
        self.session.commit()

    def __exit__(self, *_) -> None:
        self.session.close()
