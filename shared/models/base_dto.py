from abc import ABC, abstractmethod
from typing import Any

from firebase_admin.firestore import firestore as fs
from marshmallow import Schema, EXCLUDE


class BaseDTO(ABC):
    """
    Abstract base class for Data Transfer Objects.
    """

    @staticmethod
    @abstractmethod
    def id_name() -> str:
        """
        Gets the name of the ID field for the DTO.
        """
        pass

    @abstractmethod
    def id_value(self) -> str:
        """
        Gets the value of the ID field in the DTO object.
        """
        pass


class BaseDTOFactory(ABC):
    """
    Provides a base implementation for creating DTO objects from Firestore DocumentSnapshots.
    """

    @staticmethod
    @abstractmethod
    def create_from_doc(doc_snapshot: fs.DocumentSnapshot) -> Any:
        """
        Create an instance of the derived class from a given DocumentSnapshot.

        :param doc_snapshot: The DocumentSnapshot object to create the instance from.
        :return: An instance of the derived class created from the DocumentSnapshot.
        """
        pass

    @staticmethod
    def doc_to_object(schema: Schema, doc_snapshot: fs.DocumentSnapshot, id_name: str) -> Any | None:
        """
        Converts a Google Cloud Firestore DocumentSnapshot into a Python object.

        :param schema: The Marshmallow Schema used for deserialization.
        :param doc_snapshot: The DocumentSnapshot to convert.
        :param id_name: The name of the key to store the document ID (default: 'id').
        :return: An object representation of the DocumentSnapshot, where the key 'id_name'
                 is used to store the document ID. If doc_snapshot is None, None is returned.
        :rtype: dict[str, Any] | None
        """
        if doc_snapshot is None:
            return None

        doc_dict = {id_name: doc_snapshot.id}
        doc_dict.update(doc_snapshot.to_dict())

        dto = schema.load(doc_dict, partial=True, unknown=EXCLUDE)
        return dto
