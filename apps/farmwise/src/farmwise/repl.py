import argparse
import asyncio
import os
from pathlib import Path
from typing import Optional

from agents import ItemHelpers, Runner
from dotenv import load_dotenv
from farmbase_client.models import ContactRead, OrganizationRead
from openai.types.responses import EasyInputMessageParam, ResponseInputTextParam

from farmwise.agent import DEFAULT_AGENT, agents
from farmwise.context import UserContext


def _build_user_context(name: str, phone: str, organization_slug: str = "default") -> UserContext:
    org = OrganizationRead(name=organization_slug, slug=organization_slug)
    contact = ContactRead(name=name, phone_number=phone, organization=org)
    return UserContext(contact=contact, new_user=True, memories=[])


async def _run_streamed(agent, text: str, previous_response_id: Optional[str], context: Optional[UserContext]):
    input_items = [
        EasyInputMessageParam(
            role="user",
            content=[ResponseInputTextParam(type="input_text", text=text)],
        )
    ]

    result = Runner.run_streamed(
        agent,
        input=input_items,
        previous_response_id=previous_response_id,
        context=context,
    )

    async for event in result.stream_events():
        if event.type == "run_item_stream_event" and event.item.type == "message_output_item":
            chunk = ItemHelpers.text_message_output(event.item)
            if chunk:
                print(chunk, end="", flush=True)
    print()

    return result


async def _run_sync(agent, text: str, previous_response_id: Optional[str], context: Optional[UserContext]):
    res = await Runner.run(agent, text, previous_response_id=previous_response_id, context=context)
    print(res.final_output)
    return res


SESS_DIR = Path(os.environ.get("FARMWISE_SESS_DIR", Path.home() / ".farmwise" / "sessions"))


def _load_previous_response_id(session_id: Optional[str]) -> Optional[str]:
    if not session_id:
        return None
    path = SESS_DIR / f"{session_id}.txt"
    try:
        return path.read_text().strip() or None
    except FileNotFoundError:
        return None


def _save_previous_response_id(session_id: Optional[str], response_id: Optional[str]) -> None:
    if not session_id or not response_id:
        return
    SESS_DIR.mkdir(parents=True, exist_ok=True)
    (SESS_DIR / f"{session_id}.txt").write_text(response_id)


async def chat(
    agent_name: Optional[str],
    message: Optional[str],
    session_id: Optional[str],
    interactive: bool,
    name: str,
    phone: str,
    non_stream: bool = False,
):
    load_dotenv()

    agent = agents[agent_name] if agent_name else agents[DEFAULT_AGENT]
    previous_response_id: Optional[str] = _load_previous_response_id(session_id)
    context = _build_user_context(name=name, phone=phone)

    if interactive:
        print(f"Interactive chat with '{agent.name}'. Ctrl-D or 'exit' to quit.")
        try:
            while True:
                try:
                    user_text = input("> ").strip()
                except EOFError:
                    print()
                    break
                if user_text.lower() in {"exit", "quit"}:
                    break

                if non_stream:
                    res = await _run_sync(agent, user_text, previous_response_id, context)
                else:
                    res = await _run_streamed(agent, user_text, previous_response_id, context)

                previous_response_id = res.last_response_id
                _save_previous_response_id(session_id, previous_response_id)
        except KeyboardInterrupt:
            print()
            return
    else:
        if not message:
            raise SystemExit("--message is required when not using --interactive")
        if non_stream:
            res = await _run_sync(agent, message, previous_response_id, context)
        else:
            res = await _run_streamed(agent, message, previous_response_id, context)

        previous_response_id = res.last_response_id
        _save_previous_response_id(session_id, previous_response_id)


def list_agents():
    for key, agent in agents.items():
        print(f"{key} :: {agent.handoff_description}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="farmwise-agents",
        description="CLI to interact with Farmwise agents (OpenAI Agents SDK)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List available agents")
    p_list.set_defaults(func=lambda args: list_agents())

    p_chat = sub.add_parser("chat", help="Chat with an agent")
    p_chat.add_argument("--agent", "-a", help="Agent name (defaults to triage/default)")
    p_chat.add_argument("--message", "-m", help="One-shot message (omit for interactive mode)")
    p_chat.add_argument("--interactive", "-i", action="store_true", help="Interactive REPL mode")
    p_chat.add_argument(
        "--session",
        "-s",
        help="Thread id for previous_response_id continuity (e.g. user_123)",
    )
    p_chat.add_argument("--name", default=os.environ.get("FW_NAME", "CLI User"), help="User name for context")
    p_chat.add_argument("--phone", default=os.environ.get("FW_PHONE", "+0000000000"), help="Phone for context")
    p_chat.add_argument("--non-stream", action="store_true", help="Disable streaming; print final output only")

    async def _chat_wrapper(args):
        await chat(
            agent_name=args.agent,
            message=args.message,
            session_id=args.session,
            interactive=args.interactive or (args.message is None),
            name=args.name,
            phone=args.phone,
            non_stream=args.non_stream,
        )

    p_chat.set_defaults(async_func=_chat_wrapper)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Run async handler if present
    if hasattr(args, "async_func"):
        asyncio.run(args.async_func(args))
    else:
        args.func(args)


if __name__ == "__main__":
    main()
