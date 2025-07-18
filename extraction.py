import getpass
import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


class Authors(BaseModel):
    """A list of authors, each with their own information."""

    first_author: str = Field(
        description="The full name of the first author in the list.",
    )

    co_authors: Optional[str] = Field(
        default_factory=str,
        description="A list of co-authors, if any, who are not the first author.",
    )


prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. You will receive an "
            "string with the author or authors of a book and you will return "
            "the first author and if there are more than one, you will "
            "return the rest of the authors as co-authors. "
            "You will return the authors in a structured format."
            "Ignore the By at the beginning of the string.",
        ),
        ("human", "{authors}"),
    ]
)


if not os.environ.get("ANTHROPIC_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = getpass.getpass(
        "Enter API key for Anthropic: "
    )


llm = init_chat_model("claude-3-5-sonnet-latest", model_provider="anthropic")
structured_llm = llm.with_structured_output(schema=Authors)


if __name__ == "__main__":
    prompt = prompt_template.invoke(
        {
            "authors": "By Luigi & David Fastuca with Eduardo Rodriguez and John Ayers"
        }
    )
    authors = structured_llm.invoke(prompt)
    print(authors)
