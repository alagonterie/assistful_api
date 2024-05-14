from typing import Optional, cast

from flask import request
from google.oauth2 import service_account
from jsonpickle import decode
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatVertexAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.vectorstores import Chroma

from shared.globals.constants import MAX_OUTPUT_TOKENS, AUTH_HEADER_NAME
from shared.globals.objects import FIREBASE_CREDS
from shared.models.ai.agents.tools.assistful_nla_tool import AssistfulNLATool
from shared.models.ai.agents.tools.utils.assistful_api_operation import AssistfulAPIOperation

# TODO: wrap all this into a class with a class method like AssistfulAgent.from_...(...)
# TODO:     the agent should not make calls to fs itself. fs resources go in the from... method?
# TODO: these are called agents internally, but assistants externally

vector_store: Optional[Chroma] = None  # TODO: this is only for testing
chat_history: Optional[MessagesPlaceholder] = None  # TODO: this is only for testing
memory: Optional[ConversationBufferMemory] = None  # TODO: this is only for testing

MEMORY_KEY: str = 'chat_history'
API_OPERATION_KEY: str = 'encoded_api_operation'


def query_test_agent(user_query: str) -> str:
    _create_tool_vector_store_if_not_exists()

    tool_memory: set[str] = set()
    relevant_tools: list[AssistfulNLATool] = _get_relevant_tools_from_vector_store(user_query, tool_memory)

    # TODO: need to store this memory in firestore probably
    # TODO: also need a more efficient memory model for large memory
    global chat_history
    global memory
    if not chat_history or not memory:
        chat_history = MessagesPlaceholder(variable_name=MEMORY_KEY)
        memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)

    chat_llm = ChatVertexAI(**{
        # TODO: 'tuned_model_name': GCP_TUNED_MODEL_DOCS2REQUESTS
        'credentials': service_account.Credentials.from_service_account_info(FIREBASE_CREDS),
        'max_output_tokens': MAX_OUTPUT_TOKENS
    })

    # "all_relevant_tools" once api specs are being combined?
    agent_executor = initialize_agent(
        relevant_tools,
        chat_llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        agent_kwargs={
            'input_variables': ['input', 'agent_scratchpad', MEMORY_KEY],
            'memory_prompts': [chat_history],
        },
        verbose=True
    )

    # TODO: need a special callback handler with class level variables to store/access metadata during tool chaining.
    from shared.models.ai.callbacks.tool_memory_callback_handler import ToolMemoryCallbackHandler
    handler = ToolMemoryCallbackHandler(tool_memory=tool_memory)

    chain_output = agent_executor.run(user_query, callbacks=[handler])
    return str(chain_output)


def clear_vector_store() -> None:
    global vector_store
    vector_store = None


def clear_memory() -> None:
    global chat_history
    global memory
    memory = None
    chat_history = None


def _create_tool_vector_store_if_not_exists() -> None:
    global vector_store
    if vector_store:
        return

    from provider.provider_modules import spec_provider
    from shared.globals.helpers import get_debug_docs_uri, get_debug_uri
    spec: dict = spec_provider.spec_from_uri(get_debug_docs_uri(), get_debug_uri())

    from langchain.tools.openapi.utils.openapi_utils import OpenAPISpec
    openapi_spec = OpenAPISpec.from_spec_dict(spec)

    from shared.models.ai.agents.toolkits.assistful_nla_toolkit import AssistfulNLAToolkit
    toolkit = AssistfulNLAToolkit.from_spec(openapi_spec)

    from langchain.schema import Document
    from jsonpickle import encode
    docs: list[Document] = []
    for tool in toolkit.nla_tools:
        doc = Document(
            page_content=tool.description,
            metadata={API_OPERATION_KEY: encode(tool.api_operation)}
        )
        docs.append(doc)

    from langchain.embeddings import VertexAIEmbeddings
    vector_store = Chroma.from_documents(docs, VertexAIEmbeddings())  # TODO: switch to Redis from Chroma


def _get_relevant_tools_from_vector_store(user_query: str, tool_memory: set[str]) -> list[AssistfulNLATool]:
    global vector_store
    if not vector_store:
        raise ValueError('There is no vector store')

    if memory:
        # Recent chat history should be used for selecting relevant tools and for running the tool functions.
        messages = memory.chat_memory.messages
        messages_content = [message.content for message in messages] if messages else []
        user_query = '\n'.join([user_query] + messages_content[-2:])

    # Longer queries are given more than the default 4 tools.
    min_k = 4
    max_k = 8
    word_count_per_k = 8
    word_count = len(user_query.split())
    k = min(word_count // word_count_per_k + min_k, max_k)

    retriever = vector_store.as_retriever(search_kwargs={'k': k})
    relevant_tool_docs = retriever.get_relevant_documents(user_query)

    headers = {AUTH_HEADER_NAME: request.headers.get(AUTH_HEADER_NAME)}
    return [
        AssistfulNLATool.from_query_and_api_operation(
            user_query,
            cast(AssistfulAPIOperation, decode(relevant_tool_doc.metadata[API_OPERATION_KEY])),
            tool_memory=tool_memory,
            headers=headers
        )
        for relevant_tool_doc in relevant_tool_docs
    ]
