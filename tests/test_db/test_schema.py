import pytest
from pydantic import ValidationError

from unfazed.schema.orm import (
    BaseCredential,
    Connection,
    Database,
    MysqlCredential,
    PgsqlCredential,
    SqliteCredential,
)


class TestSqliteCredential:
    def test_validate_all_pragmas(self) -> None:
        cred = SqliteCredential.model_validate(
            {
                "FILE_PATH": "test.db",
                "JOURNAL_MODE": "WAL",
                "JOURNAL_SIZE_LIMIT": 16384,
                "FOREIGN_KEYS": "ON",
                "SYNCHRONOUS": "NORMAL",
                "BUSY_TIMEOUT": 5000,
                "CACHE_SIZE": -2000,
                "TEMP_STORE": 2,
                "WAL_AUTOCHECKPOINT": 1000,
                "MMAP_SIZE": 268435456,
                "LOCKING_MODE": "NORMAL",
            }
        )

        assert cred.file_path == "test.db"
        assert cred.journal_mode == "WAL"
        assert cred.journal_size_limit == 16384
        assert cred.foreign_keys == "ON"
        assert cred.synchronous == "NORMAL"
        assert cred.busy_timeout == 5000
        assert cred.cache_size == -2000
        assert cred.temp_store == 2
        assert cred.wal_autocheckpoint == 1000
        assert cred.mmap_size == 268435456
        assert cred.locking_mode == "NORMAL"

    def test_file_path_is_required(self) -> None:
        with pytest.raises(ValidationError):
            SqliteCredential.model_validate({"SYNCHRONOUS": "NORMAL"})

    def test_dump_excludes_unset_pragmas(self) -> None:
        cred = SqliteCredential.model_validate({"FILE_PATH": "test.db"})

        assert cred.model_dump(exclude_none=True) == {"file_path": "test.db"}


class TestBaseCredential:
    def test_pool_size_defaults_to_none(self) -> None:
        cred = BaseCredential.model_validate(
            {"USER": "u", "PASSWORD": "p", "HOST": "h", "PORT": 5432, "DATABASE": "d"}
        )

        assert cred.minsize is None
        assert cred.maxsize is None
        assert cred.model_dump(exclude_none=True) == {
            "user": "u",
            "password": "p",
            "host": "h",
            "port": 5432,
            "database": "d",
        }


class TestPgsqlCredential:
    def test_validate_all_params(self) -> None:
        cred = PgsqlCredential.model_validate(
            {
                "USER": "u",
                "PASSWORD": "p",
                "HOST": "h",
                "PORT": 5432,
                "DATABASE": "d",
                "MIN_SIZE": 2,
                "MAX_SIZE": 10,
                "MAX_QUERIES": 50000,
                "MAX_INACTIVE_CONNECTION_LIFETIME": 300.0,
                "SSL": True,
                "COMMAND_TIMEOUT": 2.5,
                "TIMEOUT": 10,
                "STATEMENT_CACHE_SIZE": 200,
                "MAX_CACHED_STATEMENT_LIFETIME": 600,
                "MAX_CACHEABLE_STATEMENT_SIZE": 2048,
                "APPLICATION_NAME": "myapp",
                "SERVER_SETTINGS": {"search_path": "public"},
            }
        )

        assert cred.ssl is True
        assert cred.command_timeout == 2.5
        assert cred.timeout == 10.0
        assert cred.statement_cache_size == 200
        assert cred.max_cached_statement_lifetime == 600
        assert cred.max_cacheable_statement_size == 2048
        assert cred.application_name == "myapp"
        assert cred.server_settings == {"search_path": "public"}

    def test_ssl_accepts_bool(self) -> None:
        cred = PgsqlCredential.model_validate(
            {
                "USER": "u",
                "PASSWORD": "p",
                "HOST": "h",
                "PORT": 5432,
                "DATABASE": "d",
                "SSL": False,
            }
        )
        assert cred.ssl is False

    def test_timeout_accepts_float(self) -> None:
        cred = PgsqlCredential.model_validate(
            {
                "USER": "u",
                "PASSWORD": "p",
                "HOST": "h",
                "PORT": 5432,
                "DATABASE": "d",
                "COMMAND_TIMEOUT": 0.5,
            }
        )
        assert cred.command_timeout == 0.5

    def test_dump_excludes_unset_params(self) -> None:
        cred = PgsqlCredential.model_validate(
            {"USER": "u", "PASSWORD": "p", "HOST": "h", "PORT": 5432, "DATABASE": "d"}
        )

        assert cred.model_dump(exclude_none=True) == {
            "user": "u",
            "password": "p",
            "host": "h",
            "port": 5432,
            "database": "d",
        }


class TestMysqlCredential:
    def test_validate_all_params(self) -> None:
        cred = MysqlCredential.model_validate(
            {
                "USER": "u",
                "PASSWORD": "p",
                "HOST": "h",
                "PORT": 3306,
                "DATABASE": "d",
                "CONNECT_TIMEOUT": 10,
                "CHARSET": "utf8mb4",
                "SSL": {"ca": "/etc/ssl/certs/ca.pem"},
                "ECHO": False,
                "POOL_RECYCLE": 3600,
                "READ_TIMEOUT": 30,
                "USE_UNICODE": True,
                "INIT_COMMAND": "SET time_zone='+8:00'",
                "SQL_MODE": "STRICT_TRANS_TABLES",
            }
        )

        assert cred.connect_timeout == 10
        assert cred.charset == "utf8mb4"
        assert cred.ssl == {"ca": "/etc/ssl/certs/ca.pem"}
        assert cred.echo is False
        assert cred.pool_recycle == 3600
        assert cred.read_timeout == 30
        assert cred.use_unicode is True
        assert cred.init_command == "SET time_zone='+8:00'"
        assert cred.sql_mode == "STRICT_TRANS_TABLES"

    def test_ssl_accepts_dict(self) -> None:
        cred = MysqlCredential.model_validate(
            {
                "USER": "u",
                "PASSWORD": "p",
                "HOST": "h",
                "PORT": 3306,
                "DATABASE": "d",
                "SSL": {"ca": "/ca.pem", "cert": "/cert.pem"},
            }
        )
        assert cred.ssl == {"ca": "/ca.pem", "cert": "/cert.pem"}

    def test_dump_excludes_unset_params(self) -> None:
        cred = MysqlCredential.model_validate(
            {"USER": "u", "PASSWORD": "p", "HOST": "h", "PORT": 3306, "DATABASE": "d"}
        )

        assert cred.model_dump(exclude_none=True) == {
            "user": "u",
            "password": "p",
            "host": "h",
            "port": 3306,
            "database": "d",
        }


class TestCredentialUnion:
    def test_ssl_bool_discriminates_pgsql(self) -> None:
        conn = Connection.model_validate(
            {
                "ENGINE": "tortoise.backends.asyncpg",
                "CREDENTIALS": {
                    "USER": "u",
                    "PASSWORD": "p",
                    "HOST": "h",
                    "PORT": 5432,
                    "DATABASE": "d",
                    "SSL": True,
                    "MAX_QUERIES": 50000,
                },
            }
        )
        assert isinstance(conn.credentials, PgsqlCredential)

    def test_ssl_dict_discriminates_mysql(self) -> None:
        conn = Connection.model_validate(
            {
                "ENGINE": "tortoise.backends.mysql",
                "CREDENTIALS": {
                    "USER": "u",
                    "PASSWORD": "p",
                    "HOST": "h",
                    "PORT": 3306,
                    "DATABASE": "d",
                    "SSL": {"ca": "/ca.pem"},
                    "CHARSET": "utf8mb4",
                },
            }
        )
        assert isinstance(conn.credentials, MysqlCredential)

    def test_file_path_discriminates_sqlite(self) -> None:
        conn = Connection.model_validate(
            {
                "ENGINE": "tortoise.backends.sqlite",
                "CREDENTIALS": {"FILE_PATH": "test.db"},
            }
        )
        assert isinstance(conn.credentials, SqliteCredential)


class TestRemovedFields:
    def test_autocommit_is_not_a_field(self) -> None:
        assert "autocommit" not in MysqlCredential.model_fields

    def test_schema_is_not_a_field(self) -> None:
        assert "schema" not in PgsqlCredential.model_fields

    def test_autocommit_input_is_ignored(self) -> None:
        cred = MysqlCredential.model_validate(
            {
                "USER": "u",
                "PASSWORD": "p",
                "HOST": "h",
                "PORT": 3306,
                "DATABASE": "d",
                "AUTOCOMMIT": True,
            }
        )
        assert "autocommit" not in cred.model_dump(exclude_none=True)


class TestDatabaseDump:
    def test_model_dump_produces_tortoise_keys(self) -> None:
        db = Database.model_validate(
            {
                "CONNECTIONS": {
                    "default": {
                        "ENGINE": "tortoise.backends.asyncpg",
                        "CREDENTIALS": {
                            "USER": "u",
                            "PASSWORD": "p",
                            "HOST": "h",
                            "PORT": 5432,
                            "DATABASE": "d",
                            "SSL": True,
                            "SERVER_SETTINGS": {"search_path": "public"},
                        },
                    }
                }
            }
        )

        dumped = db.model_dump(exclude_none=True)
        credentials = dumped["connections"]["default"]["credentials"]

        assert credentials["ssl"] is True
        assert credentials["server_settings"] == {"search_path": "public"}
        # aliases are resolved to Tortoise expected lowercase keys
        assert "SSL" not in credentials
        assert "SERVER_SETTINGS" not in credentials
