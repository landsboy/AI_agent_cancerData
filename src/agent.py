from __future__ import annotations
from langchain_perplexity import ChatPerplexity
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

from .prompts import AGENT_PROMPT
from .tools import make_pubmed_tool, make_web_tool, make_safe_get_tool
from .http_client import _is_allowed
# ----------------------------
# LLM Wrapper (Perplexity)
# ----------------------------
class PatchedChatPerplexity(ChatPerplexity):
    """Remove stop/stop_sequences everywhere to avoid API mismatch."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("streaming", False)
        kwargs.pop("stop", None)
        kwargs.pop("stop_sequences", None)
        mk = kwargs.get("model_kwargs")
        if isinstance(mk, dict):
            mk.pop("stop", None)
            mk.pop("stop_sequences", None)
        eb = kwargs.get("extra_body")
        if isinstance(eb, dict):
            eb.pop("stop", None)
            eb.pop("stop_sequences", None)
        super().__init__(*args, **kwargs)

    def _strip_stops_everywhere(self, kwargs: dict) -> dict:
        kwargs.pop("stop", None)
        kwargs.pop("stop_sequences", None)
        for key in ("extra_body", "model_kwargs", "params"):
            d = kwargs.get(key)
            if isinstance(d, dict):
                d.pop("stop", None)
                d.pop("stop_sequences", None)
        # also strip attributes
        try:
            mk = dict(getattr(self, "model_kwargs", {}) or {})
            mk.pop("stop", None)
            mk.pop("stop_sequences", None)
            object.__setattr__(self, "model_kwargs", mk)
        except Exception:
            pass
        try:
            eb = dict(getattr(self, "extra_body", {}) or {})
            eb.pop("stop", None)
            eb.pop("stop_sequences", None)
            object.__setattr__(self, "extra_body", eb)
        except Exception:
            pass
        return kwargs

    def _generate(self, messages, stop=None, **kwargs):
        kwargs = self._strip_stops_everywhere(kwargs)
        return super()._generate(messages, stop=None, **kwargs)

    def _stream(self, messages, stop=None, **kwargs):
        kwargs = self._strip_stops_everywhere(kwargs)
        return super()._stream(messages, stop=None, **kwargs)




def build_agent(
    n_results: int,
    temperature: float,
    mindate: str | None,
    maxdate: str | None,
    disease_clause: str | None,
    disease_name: str,
    *,
    tools=None,
    prompt_template: str = AGENT_PROMPT,   # <-- ברירת מחדל
) -> AgentExecutor:
    llm = PatchedChatPerplexity(model="sonar-pro", temperature=temperature)

    # אם לא הועברו כלים — נבנה כאן
    if tools is None:
        pubmed_tool = make_pubmed_tool(mindate, maxdate, disease_clause or "")
        web_tool = make_web_tool()
        safe_get_tool = make_safe_get_tool(_is_allowed)
        tools = [pubmed_tool, web_tool, safe_get_tool]

    tmpl = PromptTemplate.from_template(prompt_template)
    date_hint = f"{mindate or 'NA'}..{maxdate or 'NA'}" if (mindate or maxdate) else "none"

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=tmpl.partial(
            n_results=n_results,
            date_hint=date_hint,
            disease_name=disease_name,
        ),
    )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=24,
        early_stopping_method="generate",
    )