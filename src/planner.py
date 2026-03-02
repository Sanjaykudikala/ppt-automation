"""Planner node — uses LLM to plan slides with theme, layout, and premise."""

from langchain_core.prompts import ChatPromptTemplate

from src.config import invoke_with_retry
from src.models import PresentationPlan
from src.prompts import get_planner_prompt


def plan_presentation(llm, topic: str, num_slides: int, audience_type: str) -> PresentationPlan:
    """
    Generate a presentation plan using the LLM.

    Parameters
    ----------
    llm : ChatGroq
        The LLM instance.
    topic : str
        Topic for the presentation.
    num_slides : int
        Number of slides to generate.
    audience_type : str
        One of 'beginner', 'intermediate', 'advanced'.

    Returns
    -------
    PresentationPlan
        Structured plan with theme and slide definitions.
    """
    system_prompt = get_planner_prompt(audience_type)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Create a {num_slides} slide presentation about: {topic}."),
    ])

    messages = prompt.format_messages(num_slides=num_slides, topic=topic)

    return invoke_with_retry(llm, messages, structured_output=PresentationPlan)
