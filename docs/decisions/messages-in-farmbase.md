date: 2025-05-12

Message history could be maintained using the OpenAI responses API. 

However, this is not compatible with other model providers.

OpenAI only supports 30 days of message history. 

We also need to merge (by time), messages that are sent by scheduled tasks. 

We also need to compress context of messages over time. 

We also need to make messages available to the FarmBase UI.

Therefore,

Messages will be stored in the FarmBase database, and updated via the API.

