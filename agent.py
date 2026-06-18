from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from tools import send_email, write_email_reply
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


OPENAI_MODEL = os.getenv("OPENAI_MODEL")

agent = create_agent(
    model=ChatOpenAI(model=OPENAI_MODEL),
    tools=[send_email, write_email_reply],
    checkpointer=MemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                'send_email': {
                    "allowed_decisions": ["approve", "edit", "reject"],
                    'questions': ["Do you want to send the email?"]
                },
                "write_email_reply": False,
            }
        )
    ]
)


