import typing

class UserRepository:
    def __init__(self):
        self._users = {}

    def create(self, email: str, details: dict[str, typing.Any]):
        self._users[email] = details

    def get(self, email: str) -> dict[str, typing.Any] | None:
        return self._users.get(email)

    def update(self, email: str, details: dict[str, typing.Any]):
        self._users[email] = details

    def delete(self, email: str):
        del self._users[email]

    def exists(self, email: str) -> bool:
        return email in self._users

    def is_password_valid(self, email: str, password: str) -> bool:
        return self._users[email]["password"] == password

user_repository = UserRepository()  # create an instance of the user repository