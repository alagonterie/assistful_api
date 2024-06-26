RESPONSE_PREFIX: str = 'Responded with: '
ASSISTFUL_REQUEST_TEMPLATE = """You are a helpful AI Assistant. Please provide JSON arguments to agentFunc() based on the user's instructions.

API_SCHEMA: ```typescript
{schema}
```

USER_INSTRUCTIONS: "{instructions}"

Your arguments must be plain json provided in a markdown block:

ARGS: ```json
{{valid json conforming to API_SCHEMA}}
```

Example
-----

ARGS: ```json
{{"foo": "bar", "baz": {{"qux": "quux"}}}}
```

The block must be no more than 1 line long, and all arguments must be valid JSON. All string arguments must be wrapped in double quotes.
You MUST strictly comply to the types indicated by the provided schema, including all REQUIRED args.

If you don't have sufficient information to call the function due to things like missing REQUIRED args, you can reply with the following message:

Message: ```text
Concise response requesting the additional information that would make calling the function successful.
```

Begin
-----
ARGS:
"""
