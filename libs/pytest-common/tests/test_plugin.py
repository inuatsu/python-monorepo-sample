from os import environ


def test_single_process(pytester):
    # シングルプロセス実行のテスト
    pytester.makepyfile(
        """
        from subprocess import check_output

        from factory.alchemy import SQLAlchemyModelFactory
        from pytest import fixture
        from sqlalchemy import create_engine, inspect

        from pytest_common.factories.edinet_companies import EdinetCompanyFactory
        from pytest_common.plugin import ORMS


        def test_docker_container_count():
            # Check the number of started Docker container is one
            res =check_output([
                "docker", "container", "ls", "-q", "--filter", "label=com.docker.compose.project=pytest_common"
            ]).decode("utf-8").strip()
            containers = res.split("\\n")
            assert len(containers) == 1

        def test_database_count(docker_ip, docker_port):
            # Check the number of database in MySQL Docker container is one
            engine = create_engine(
                f"mysql+mysqlconnector://root:password@{docker_ip}:{docker_port}", echo=False, pool_recycle=60,
            )
            databases = inspect(engine).get_schema_names()
            assert [db for db in databases if db.startswith("test_")] == ["test_gw0"]


        def test_create_table(engine):
            # Check tables are created in MySQL Docker container
            assert set(inspect(engine).get_table_names()) == set([orm.__tablename__ for orm in ORMS])


        def test_factory(session):
            # Check SQLAlchemy session is set and session_persistence is `flush` in factories' Meta class
            EdinetCompanyFactory.build()
            factory_classes = SQLAlchemyModelFactory.__subclasses__()
            assert len(factory_classes) > 0
            for cls in factory_classes:
                assert cls._meta.sqlalchemy_session == session
                assert cls._meta.sqlalchemy_session_persistence == "flush"
        """
    )

    environ["VOLUME_CLEANUP"] = "true"
    result = pytester.runpytest()
    result.assert_outcomes(passed=4)


def test_multiprocess(pytester):
    # マルチプロセス実行のテスト
    pytester.makepyfile(
        """
        from subprocess import check_output

        from factory.alchemy import SQLAlchemyModelFactory
        from pytest import fixture
        from sqlalchemy import create_engine, inspect

        from pytest_common.factories.edinet_companies import EdinetCompanyFactory
        from pytest_common.plugin import ORMS


        def test_docker_container_count():
            # Check the number of started Docker container is one
            res =check_output([
                "docker", "container", "ls", "-q", "--filter", "label=com.docker.compose.project=pytest_common"
            ]).decode("utf-8").strip()
            containers = res.split("\\n")
            assert len(containers) == 1

        def test_database_count(docker_ip, docker_port):
            # Check the number of database in MySQL Docker container is two
            engine = create_engine(
                f"mysql+mysqlconnector://root:password@{docker_ip}:{docker_port}", echo=False, pool_recycle=60
            )
            databases = inspect(engine).get_schema_names()
            assert set([db for db in databases if db.startswith("test_")]) == set(["test_gw0", "test_gw1"])


        def test_create_table(docker_ip, docker_port):
            # Check tables are created in each MySQL Docker container
            uname = "test_admin"
            pw = "password"
            charset = "utf8mb4"
            collation = "utf8mb4_general_ci"

            engine1 = create_engine(
                f"mysql+mysqlconnector://{uname}:{pw}@{docker_ip}:{docker_port}/test_gw0?charset={charset}&collation={collation}",
                echo=False,
                pool_recycle=60,
            )
            engine2 = create_engine(
                f"mysql+mysqlconnector://{uname}:{pw}@{docker_ip}:{docker_port}/test_gw1?charset={charset}&collation={collation}",
                echo=False,
                pool_recycle=60,
            )

            assert set(inspect(engine1).get_table_names()) == set([orm.__tablename__ for orm in ORMS])
            assert set(inspect(engine2).get_table_names()) == set([orm.__tablename__ for orm in ORMS])


        def test_factory(session):
            # Check SQLAlchemy session is set and session_persistence is `flush` in factories' Meta class
            EdinetCompanyFactory.build()
            factory_classes = SQLAlchemyModelFactory.__subclasses__()
            assert len(factory_classes) > 0
            for cls in factory_classes:
                assert cls._meta.sqlalchemy_session == session
                assert cls._meta.sqlalchemy_session_persistence == "flush"
        """
    )

    environ["VOLUME_CLEANUP"] = "true"
    result = pytester.runpytest("--numprocesses=2")
    result.assert_outcomes(passed=4)
