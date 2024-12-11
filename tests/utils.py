import pymysql
import pymysql.cursors


class DataBase:
    def __init__(self, host: str, port: int, root_user: str, password: str) -> None:
        self._host = host
        self._port = port
        self._user = root_user
        self._password = password

    def connect(self) -> pymysql.connections.Connection:
        connection = pymysql.connect(
            host=self._host,
            user=self._user,
            port=self._port,
            password=self._password,
            cursorclass=pymysql.cursors.DictCursor,
        )
        return connection

    def create_db(self, db_name: str) -> None:
        conn = self.connect()

        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE {db_name}  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )

            conn.commit()

    def drop_db(self, db_name: str) -> None:
        conn = self.connect()

        with conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DROP DATABASE {db_name}")

            conn.commit()
