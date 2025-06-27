from farmwise.context import UserContext


def get_profile_and_memories(context: UserContext):
    return f"""
This is the profile of the user you are speaking with: {context.contact}

These are the stored memories for this user. Give more weight to the question by users and try to answer that first. 
You can modify your answer based on these memories. If the memories are irrelevant you should ignore them. 
Also don't reply to this section of the prompt, or the memories, they are only for your reference.
{"\n".join([m.memory for m in context.memories])}    
    """
