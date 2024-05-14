from http import HTTPStatus
from typing import TypeVar, Generic

import flask

from firebase_admin.firestore import firestore as fs

from shared.globals import constants
from shared.globals.constants import OWNER_ID, FIELD_ORG_ID, TYPE_NAME_ORG
from shared.globals.enums import AccessLevels
from shared.models.base_dto import BaseDTOFactory, BaseDTO
from shared.models.security.user_context import UserContext

T_DTO = TypeVar('T_DTO', BaseDTO, None)


class GenericRepo(Generic[T_DTO]):
    def __init__(self, doc_type_name: str, collection_ref: fs.CollectionReference, dto_factory: type[BaseDTOFactory]):
        self.doc_type_name = doc_type_name
        self.collection_ref = collection_ref
        self.dto_factory = dto_factory

    def get(self, ctx: UserContext, doc_id: str) -> T_DTO | None:
        """
        Get a document by its ID.

        :param ctx: The user context for the request.
        :param doc_id: The ID of the document to get.
        :return: The document object with the given ID, or None if not found.
        :raises flask.abort(404): If the document does not exist.
        """
        doc_snap = self._validate_doc(ctx, doc_id)
        doc_object: T_DTO = self.dto_factory.create_from_doc(doc_snap)
        return doc_object

    def get_all(self, ctx: UserContext) -> list[T_DTO | None]:
        """
        Retrieve all documents from the collection.

        :param ctx: The user context for the request.
        :return: A list of instances of T_DTO representing the retrieved documents.
                 If no documents are found, an empty list is returned.
                 If there is an error retrieving the documents, None is returned.
        """
        ctx.abort_if_insufficient_access(AccessLevels.ADMIN)

        return [self.dto_factory.create_from_doc(doc_snap) for doc_snap in self.collection_ref.get()]

    def insert(self, ctx: UserContext, insert_dto: T_DTO) -> str:
        """
        Inserts a new document into the database collection.

        :param ctx: The user context for the request.
        :param insert_dto: An instance of a data transfer object (DTO) representing the document to be inserted.
        :return: The ID of the newly created document.
        """
        insert_dto_dict = {k: v for k, v in insert_dto.__dict__.items() if k != insert_dto.id_name()}
        if insert_dto.id_name() != constants.FIELD_ORG_ID and ctx.org_id is not None:
            insert_dto_dict[constants.FIELD_ORG_ID] = ctx.org_id

        insert_dto_dict[constants.FIELD_INSERT_USER] = OWNER_ID if ctx.user_id is None else ctx.user_id

        _, new_doc_ref = self.collection_ref.add(insert_dto_dict)
        return new_doc_ref.id

    def update(self, ctx: UserContext, update_dto: T_DTO, ignore_none: bool = True) -> None:
        """
        This method updates a document in the Firestore database with the provided data from the update_dto parameter.
        It uses the update_dto's dto_id property as the document ID.

        The update_dto properties are converted to a dictionary,
        excluding the dto_id property and any properties with None values if the ignore_none parameter is set to True.
        The document in the Firestore collection with the corresponding document ID is then updated with the new data.

        :param ctx: The user context for the request.
        :param update_dto: The data transfer object that contains the updated data.
        :param ignore_none: Optional parameter to indicate whether to ignore properties with None values or not.
                            Default is True.
        :raises flask.abort(404): If the document does not exist.
        """
        update_dto_dict = {k: v for k, v in update_dto.__dict__.items() if
                           k not in [update_dto.id_name(), constants.FIELD_ORG_ID] and (ignore_none or v is not None)}
        update_dto_dict[constants.FIELD_UPDATE_USER] = OWNER_ID if ctx.user_id is None else ctx.user_id

        doc_snap = self._validate_doc(ctx, update_dto.id_value())
        doc_snap.reference.update(update_dto_dict)

    def add_elements(self, ctx: UserContext, doc_id: str, array_field_name: str, new_elements: list[str]) -> None:
        """
        :param ctx: UserContext object containing user information
        :param doc_id: str representing the ID of the document in Firestore
        :param array_field_name: str representing the name of the array field in the document
        :param new_elements: A list of str representing the new elements to be added to the array field
        :return: None

        The add_elements method is used to add new elements to an array field in a Firestore document.
        It takes in the user context, document ID, array field name, and new elements as parameters.
        """
        doc_snap = self._validate_doc(ctx, doc_id)
        if doc_snap is None or not doc_snap.exists:
            return

        array_field_value = doc_snap.get(array_field_name)
        if array_field_value is None:
            raise Exception(f'The {array_field_name} field does not exist on the {self.doc_type_name} type')

        array_field_value += new_elements
        doc_snap.reference.update({array_field_name: array_field_value})

    def delete(self, ctx: UserContext, doc_id: str) -> None:
        """
        Delete a document from the Firestore collection.

        :param ctx: The user context for the request.
        :param doc_id: The ID of the document to be deleted.
        :raises flask.abort(404): If the document does not exist.
        """
        ctx.abort_if_insufficient_access(AccessLevels.ADMIN_OWNER)

        doc_snap = self._validate_doc(ctx, doc_id)
        doc_snap.reference.delete()

    def _validate_doc(self, ctx: UserContext, doc_id: str) -> fs.DocumentSnapshot:
        """
        Validate a document by its ID. Gets document data if the document exists.

        :param ctx: The user context for the request.
        :type ctx: UserContext
        :return: A tuple containing the reference to the document and the document snapshot.
        :param doc_id: The ID of the document to validate.
        :type doc_id: str
        :return: A snapshot containing the document data.
        :rtype: DocumentSnapshot
        """
        doc_ref = self.collection_ref.document(doc_id)
        doc_snap = doc_ref.get()
        if not doc_snap.exists or not self._has_org_access_to_doc(ctx, doc_snap):
            flask.abort(HTTPStatus.NOT_FOUND, f"{self.doc_type_name} '{doc_id}' not found")

        return doc_snap

    def _has_org_access_to_doc(self, ctx: UserContext, doc_snap: fs.DocumentSnapshot):
        """
        :param ctx: The UserContext object representing the current user's context.
        :param doc_snap: The DocumentSnapshot object representing the document to check access for.
        :return: True if the user has access to the document within the organization, False otherwise.

        This method checks if the user has access to the given document within the organization.
        It returns True if the document's organization ID matches the user's organization ID,
        and if the document type is not 'Organization'.
        Otherwise, it returns False.
        """

        return self.doc_type_name == TYPE_NAME_ORG or \
            ctx.org_id is not None and \
            doc_snap.to_dict().get(FIELD_ORG_ID) == ctx.org_id
