# app.py (root)
import os
import streamlit as st
from graph import build_graph, NGState  # flat, simple import

# Optional dotenv (for local runs)
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass

st.set_page_config(page_title="newsgenie", page_icon="🧞", layout="wide")
st.title("🧞 NewsGenie — AI-Powered Information & News Assistant")

def _secret(name: str):
    val = os.environ.get(name)
    if val: return val
    try:
        return st.secrets[name]
    except Exception:
        return None

# Export secrets to env for downstream modules
for _k in ("OPENAI_API_KEY", "NEWSAPI_KEY", "TAVILY_API_KEY"):
    _v = _secret(_k)
    if _v: os.environ[_k] = _v

_missing = [k for k in ("OPENAI_API_KEY","NEWSAPI_KEY") if not os.environ.get(k)]
with st.sidebar:
    st.header("Settings")
    if _missing:
        st.error("Server keys not configured. Set environment variables before launch.")
    else:
        st.success("Server is configured.")

if _missing:
    st.stop()

if "chat" not in st.session_state:
    st.session_state.chat = []
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

def coerce_state(result):
    if isinstance(result, dict):
        try:
            return NGState(**result)
        except Exception:
            return NGState(
                query=result.get("query",""),
                intent=result.get("intent"),
                category=result.get("category"),
                news=result.get("news"),
                web_results=result.get("web_results"),
                answer=result.get("answer"),
                errors=result.get("errors") or [],
            )
    return result

with st.expander("🗞️ Quick News Feeds", expanded=False):
    st.write("Select a category and click **Get Latest** to fetch a digest.")
    base = ["technology","finance","sports","business","science","health","entertainment","politics","world"]
    cat = st.selectbox("Category", base, index=0, key="quick_cat")
    if st.button("Get Latest", key="get_latest_btn"):
        state = NGState(query=f"latest {cat} news", intent="news", category=cat)
        result = st.session_state.graph.invoke(state)
        result = coerce_state(result)
        st.markdown("#### Digest")
        st.write(result.answer or "No summary.")
        if result.errors:
            st.warning("\n".join(result.errors))

st.markdown("---")

st.subheader("💬 Ask newsgenie")
for role, content in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(content)

user_msg = st.chat_input("Ask a question or request news (e.g., 'tech headlines', 'Explain LangGraph').")
if user_msg:
    st.session_state.chat.append(("user", user_msg))
    with st.chat_message("user"):
        st.markdown(user_msg)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            state = NGState(query=user_msg)
            result = st.session_state.graph.invoke(state)
            result = coerce_state(result)
            answer = result.answer or "I couldn't produce an answer."
            st.session_state.chat.append(("assistant", answer))
            st.markdown(answer)
            if result.errors:
                st.info("Notes:\n" + "\n".join(result.errors))

st.markdown("---")
st.caption("newsgenie demo — integrates OpenAI + NewsAPI + Tavily via a LangGraph workflow. Built with Streamlit.")

