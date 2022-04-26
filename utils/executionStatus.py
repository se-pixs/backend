from enum import Enum


class Status(Enum):
    SUCCESS, FAILURE, WARNING, UNKNOWN = range(4)

    def __str__(self):
        return self.name


class ExecutionStatus:
    """
    ExecutionStatus class.
    """

    def __init__(self):
        self.status = Status.UNKNOWN
        self.message = None

    def set_status(self, status: Status):
        self.status = status

    def set_message(self, message: str):
        self.message = message

    def get_status(self) -> Status:
        return self.status

    def get_message(self) -> str:
        return self.message
