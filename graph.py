import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

try:
    from .llm import classify_intent, summarize_news, answer_general
except ImportError:
    from llm import classify_intent, summarize_news, answer_general

try:
    from .services.news_providers import NewsAPIProvider, NewsProviderError
    from .services.web_search import TavilySearch, WebSearchError
except ImportError:
    from services.news_providers import NewsAPIProvider, NewsProviderError
    from services.web_search import TavilySearch, WebSearchError

class NGState(BaseModel):
    query: str
    intent: str | None = None
    category: str | None = None
    news: list[dict] | None = None
    web_results: list[dict] | None = None
    answer: str | None = None
    errors: List[str] = Field(default_factory=list)

def node_classify(state: NGState) -> NGState:
    result = classify_intent(state.query)
    state.intent = result["intent"]
    state.category = result["category"]
    return state

def node_fetch_news(state: NGState) -> NGState:
    provider = NewsAPIProvider()
    try:
        state.news = provider.top_headlines(state.category or "technology", limit=8)
    except NewsProviderError as e:
        state.errors.append(str(e))
        state.news = []
    return state

def node_fallback_search(state: NGState) -> NGState:
    if state.news:
        return state
    search = TavilySearch()
    try:
        state.web_results = search.search(state.query, max_results=5) if search.enabled() else []
    except WebSearchError as e:
        state.errors.append(str(e))
        state.web_results = []
    return state

def node_summarize(state: NGState) -> NGState:
    if state.news:
        ctx = "\n".join(f"- {a.get('title')} ({a.get('source')}) — {a.get('url')}" for a in state.news)
        state.answer = summarize_news(ctx, state.query)
    elif state.web_results:
        ctx = "\n".join(f"- {r.get('title')} — {r.get('url')}" for r in state.web_results)
        state.answer = summarize_news(ctx, state.query)
    else:
        state.answer = "Sorry, I couldn't find relevant news right now."
    return state

def node_answer_general(state: NGState) -> NGState:
    state.answer = answer_general(state.query)
    return state

def build_graph():
    sg = StateGraph(NGState)
    sg.add_node("classify", node_classify)
    sg.add_node("fetch_news", node_fetch_news)
    sg.add_node("fallback_search", node_fallback_search)
    sg.add_node("summarize", node_summarize)
    sg.add_node("answer_general", node_answer_general)
    sg.set_entry_point("classify")

    def route_decider(state: NGState):
        return "fetch_news" if (state.intent or "general") == "news" else "answer_general"

    sg.add_conditional_edges("classify", route_decider, {"fetch_news": "fetch_news", "answer_general": "answer_general"})
    sg.add_edge("fetch_news", "fallback_search")
    sg.add_edge("fallback_search", "summarize")
    sg.add_edge("summarize", END)
    sg.add_edge("answer_general", END)
    return sg.compile()
