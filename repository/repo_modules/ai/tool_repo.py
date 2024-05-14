import zlib
from concurrent.futures import ThreadPoolExecutor

from firebase_admin.firestore import firestore as fs

from repository.firestore import db
from shared.models.dto.tool_dto import ToolDTO

TOOL_COLLECTION = db.collection('tools')


def insert(tools: list[ToolDTO]) -> list[str]:
    """
    Insert a list of tools into Firestore.

    :param tools: list of ToolDTO objects representing the tools to be inserted
    :return: list of strings representing the generated tool IDs
    """
    batch: fs.WriteBatch = db.batch()
    tool_ids = []

    for tool in tools:
        tool_id: str = TOOL_COLLECTION.document().id
        tool_ids.append(tool_id)

        tool_ref: fs.DocumentReference = TOOL_COLLECTION.document(tool_id)

        compressed_api_operation: bytes = zlib.compress(tool.api_operation.encode())
        batch.set(tool_ref, {'api_operation': compressed_api_operation})

    batch.commit()

    return tool_ids


def get(tool_ids: list[str]) -> list[ToolDTO]:
    """
    Retrieve a list of tools based on the provided tool IDs.

    :param tool_ids: A list of tool IDs.
    :return: A list of ToolDTO objects representing the tools.
    """
    tools = []
    tool_futures = {tool_id: None for tool_id in tool_ids}

    with ThreadPoolExecutor() as executor:
        for tool_id in tool_ids:
            tool_futures[tool_id] = executor.submit(_fetch_tool, tool_id)

    for tool_id in tool_ids:
        tool_snap: fs.DocumentSnapshot = tool_futures[tool_id].result()

        if not tool_snap or not tool_snap.exists:
            continue

        tool_dict = tool_snap.to_dict()
        compressed_api_operation: bytes = tool_dict.get('api_operation')
        api_operation: str = zlib.decompress(compressed_api_operation).decode()
        tools.append(ToolDTO(
            tool_id=tool_snap.id,
            api_operation=api_operation
        ))

    return tools


def _fetch_tool(tool_id: str) -> fs.DocumentSnapshot:
    """
    Fetches a tool from the Firestore database.

    :param tool_id: The ID of the tool to fetch.
    :return: The document snapshot of the tool if it exists, otherwise None.
    """
    tool_ref: fs.DocumentReference = TOOL_COLLECTION.document(tool_id)
    tool_snap: fs.DocumentSnapshot = tool_ref.get()
    if tool_snap.exists:
        return tool_snap
