import requests


class DatabaseConnector:
    def __init__(self, database_url: str = "https://database.xrzhanggroup.com"):
        self._session = requests.session()
        if "://" not in database_url:
            self.url = f"http://{database_url}"
        else:
            self.url = database_url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def get_path(self, file_id: int):
        response = self._session.get(f"{self.url}/api/v1/data/path/{file_id}").json()
        return response

    def get_paths(self, file_ids: list[int]):
        return [self.get_path(file_id) for file_id in file_ids]


def load_from_database(file_ids: list[int] | int):
    with DatabaseConnector() as db:
        if isinstance(file_ids, int):
            data = db.get_path(file_ids)
        elif isinstance(file_ids, list):
            data = db.get_paths(file_ids)
        else:
            raise ValueError("Please provide a valid file id or a list of file ids")
    return data

