from abc import ABC, abstractmethod


class Action(ABC):
    """
    Custom action abstract class.
    """
    @staticmethod
    @abstractmethod
    def execute(parameters: dict, session_id: str):
        """
        Executes the action.

        :param parameters: Parameters of the action.
        :param session_id: Session id of the action.
        :return: status of the action
        """

    @staticmethod
    @abstractmethod
    def abort(session_id: str):
        """
        Abort action if it is running

        :param session_id: already validated session id of the user
        """
    @staticmethod
    @abstractmethod
    def get_status(session_id: str):
        """
        Get the status of the action

        :param session_id: already validated session id of the user
        :return: status of the action
        """
