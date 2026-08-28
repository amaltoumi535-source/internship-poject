"""
Slack bot entrypoint. Bridges Slack messages to the orchestrator via Socket Mode.
Run with: python -m app.slack_bot
"""

import os
import re
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain_core.messages import HumanMessage

from app.modules.orchestrator.agent import orchestrator  # triggers setup_logging() as a side effect

logger = logging.getLogger(__name__)

# Override just for slack_bolt, AFTER the orchestrator import above has already run
# setup_logging() and quieted httpx/httpcore/groq — this won't reopen that flood,
# it only makes Bolt itself verbose about what it receives over the socket.
logging.getLogger("slack_bolt").setLevel(logging.DEBUG)

slack_app = App(token=os.environ["SLACK_BOT_TOKEN"])


@slack_app.event("app_mention")
def handle_mention(event, say, client):
    logger.info("app_mention event received: %r", event.get("text", ""))

    raw_text = event.get("text", "")
    question = re.sub(r"^<@[A-Z0-9]+>\s*", "", raw_text).strip()

    if not question:
        say("Hi! Ask me something about your documents.")
        return

    channel = event["channel"]
    ts = event["ts"]

    client.reactions_add(channel=channel, timestamp=ts, name="hourglass_flowing_sand")

    try:
        logger.info("Invoking orchestrator with question: %r", question)
        result = orchestrator.invoke({"messages": [HumanMessage(content=question)]})
        answer = result["messages"][-1].content
        logger.info("Orchestrator responded successfully")
    except Exception as e:
        logger.exception("Orchestrator invocation failed")
        answer = f"Sorry, something went wrong: {e}"

    client.reactions_remove(channel=channel, timestamp=ts, name="hourglass_flowing_sand")
    say(answer)


if __name__ == "__main__":
    handler = SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
