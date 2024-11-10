import json
import re
from os import environ
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_output
from time import sleep
from timeit import default_timer
from typing import Type

from common.models.EdinetCompany import EdinetCompanyOrm
from factory.alchemy import SQLAlchemyModelFactory
from filelock import FileLock
from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeMeta, Session, declarative_base, scoped_session, sessionmaker
from sqlalchemy.sql import text

ORMS = [EdinetCompanyOrm]


@fixture(scope="session")
def xdist_worker_id() -> str:
    return environ.get("PYTEST_XDIST_WORKER", "gw0")


def get_docker_ip():
    # When talking to the Docker daemon via a UNIX socket, route all TCP
    # traffic to docker containers via the TCP loopback interface.
    docker_host = environ.get("DOCKER_HOST", "").strip()
    if not docker_host or docker_host.startswith("unix://"):
        return "127.0.0.1"

    match = re.match(r"^tcp://(.+?):\d+$", docker_host)
    if not match:
        raise ValueError('Invalid value for DOCKER_HOST: "%s".' % (docker_host,))
    return match.group(1)


@fixture(scope="session")
def docker_ip():
    """Determine the IP address for TCP connections to Docker containers."""

    return get_docker_ip()


@fixture(scope="session")
def docker_compose_file() -> Path:
    return Path(__file__).resolve().parent.joinpath("compose.yml")


@fixture(scope="session")
def docker_compose_project_name() -> str:
    return "pytest_common"


def docker_compose_up(docker_compose_file: Path, docker_compose_project_name: str) -> None:
    port = environ.get("DB_PORT", 13264)
    check_output(
        f"DB_PORT={port} docker compose -f {docker_compose_file} -p {docker_compose_project_name} up -d", shell=True
    )


def docker_compose_down(docker_compose_file: Path, docker_compose_project_name: str) -> None:
    # Don't remove containers if environment variable `SKIP_CLEANUP` is set to true
    # to shorten test execution time in local environment
    if environ.get("SKIP_CLEANUP", False):
        return

    # Remove volumes on removing containers only when environment variable `VOLUME_CLEANUP` is set to true
    # to shorten test execution time in local environment
    if environ.get("VOLUME_CLEANUP", False):
        check_output(
            f"docker compose -f {docker_compose_file} -p {docker_compose_project_name} down --volumes --remove-orphans",
            shell=True,
        )
        return

    check_output(f"docker compose -f {docker_compose_file} -p {docker_compose_project_name} down", shell=True)


@fixture(scope="session")
def execute_docker_compose_up_down(
    tmp_path_factory, worker_id, docker_compose_file: Path, docker_compose_project_name: str
):
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    up_fn = root_tmp_dir.joinpath("up.txt")
    is_container_exist_fn = root_tmp_dir.joinpath("is_container_exists.txt")

    #  Check if MySQL container already exists. If exists, skip docker compose up/down
    try:
        output = check_output(
            'docker ps -a --format "{{.Names}}" | grep -w "^pytest_common_mysql$"', stderr=STDOUT, shell=True
        )
    except CalledProcessError:
        output = b""
    with FileLock(str(is_container_exist_fn) + ".lock"):
        if not is_container_exist_fn.is_file():
            with open(is_container_exist_fn, "w") as f:
                f.write(f"{output.strip().decode('utf-8')}")

    # Execute `docker compose up` only once throughout all the test processes
    with FileLock(str(up_fn) + ".lock"):
        if not up_fn.is_file():
            if not is_container_exist_fn.read_text():
                docker_compose_up(docker_compose_file, docker_compose_project_name)

        with open(up_fn, "a" if up_fn.is_file() else "w") as f:
            f.write(f"{worker_id}\n")

    yield

    down_fn = root_tmp_dir.joinpath("down.txt")
    # Execute `docker compose down` only once after finishing all the test processes
    with FileLock(str(down_fn) + ".lock"):
        with open(down_fn, "a" if down_fn.is_file() else "w") as f:
            f.write(f"{worker_id}\n")

        len_up_fn = len(up_fn.read_text().split("\n"))
        len_down_fn = len(down_fn.read_text().split("\n"))
        if len_up_fn == len_down_fn:
            if not is_container_exist_fn.read_text():
                docker_compose_down(docker_compose_file, docker_compose_project_name)


@fixture(scope="session")
def docker_port() -> str:
    output = check_output("docker container inspect pytest_common_mysql", stderr=STDOUT, shell=True)
    res = json.loads(output)
    return res[0]["NetworkSettings"]["Ports"]["3306/tcp"][0]["HostPort"]


@fixture(scope="session")
def root_session(docker_ip, docker_port) -> Session:
    database = f"mysql+mysqlconnector://root:password@{docker_ip}:{docker_port}"
    engine = create_engine(database, echo=False, pool_recycle=60)
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return session()


@fixture(scope="session")
def wait_mysql_to_be_healthy(execute_docker_compose_up_down, root_session: Session, pause=0.5, timeout=30) -> None:
    ref = default_timer()
    now = ref

    while now - ref < timeout:
        try:
            root_session.execute(text("SELECT 1"))
            return
        except Exception:
            sleep(pause)
            now = default_timer()
    raise Exception("Timeout waiting for MySQL to be healthy")


@fixture(scope="session")
def delete_existing_database(tmp_path_factory, worker_id, root_session, wait_mysql_to_be_healthy) -> None:
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    db_fn = root_tmp_dir.joinpath("db.txt")
    with FileLock(str(db_fn) + ".lock"):
        if not db_fn.is_file():
            cmd = r"""
SELECT CONCAT('DROP DATABASE IF EXISTS `', SCHEMA_NAME, '`;')
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE SCHEMA_NAME LIKE 'test\_%';
"""
            delete_cmds = root_session.execute(text(cmd))
            for delete_cmd in delete_cmds:
                root_session.execute(text(delete_cmd[0]))
        with open(db_fn, "a" if db_fn.is_file() else "w") as f:
            f.write(f"{worker_id}\n")


@fixture(scope="session")
def engine(docker_ip, xdist_worker_id, docker_port, root_session, delete_existing_database) -> Engine:
    db_name = f"test_{xdist_worker_id}"
    uname = "test_admin"
    pw = "password"
    charset = "utf8mb4"
    collation = "utf8mb4_general_ci"

    # Create database
    cmd1 = f"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET {charset} COLLATE {collation}"
    cmd2 = f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{uname}'@'%'"
    root_session.execute(text(cmd1))
    root_session.execute(text(cmd2))

    database = f"mysql+mysqlconnector://{uname}:{pw}@{docker_ip}:{docker_port}/{db_name}?charset={charset}&collation={collation}"
    engine = create_engine(database, echo=False, pool_recycle=60)
    return engine


@fixture(scope="session")
def session(engine: Engine) -> Session:
    database_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return database_session()


@fixture(scope="session", autouse=True)
def create_table(wait_mysql_to_be_healthy, engine: Engine):
    Base: Type[DeclarativeMeta] = declarative_base()
    Base.metadata.drop_all(bind=engine, tables=[table for orm in ORMS for table in orm.metadata.tables.values()])
    Base.metadata.create_all(bind=engine, tables=[table for orm in ORMS for table in orm.metadata.tables.values()])


@fixture(autouse=True)
def set_session_for_factories(session):
    for cls in SQLAlchemyModelFactory.__subclasses__():
        cls._meta.sqlalchemy_session = session  # type: ignore
        cls._meta.sqlalchemy_session_persistence = "flush"  # type: ignore


@fixture(scope="function", autouse=True)
def rollback(session):
    session.rollback()
