from farmwise.context import UserContext


def get_profile_and_memories(context: UserContext):
    prompt = f"This is the profile of the user you are speaking with: {context.user}"

    if context.memories:
        prompt += f"\n\n{context.memories}"

    return prompt
