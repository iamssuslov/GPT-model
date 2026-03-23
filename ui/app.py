import os
from typing import Any

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def api_get(path: str) -> Any:
    response = requests.get(f"{API_BASE_URL}{path}", timeout=60)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict | None = None) -> Any:
    response = requests.post(
        f"{API_BASE_URL}{path}",
        json=payload or {},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


def api_upload(path: str, filename: str, content: bytes, mime_type: str) -> Any:
    response = requests.post(
        f"{API_BASE_URL}{path}",
        files={"file": (filename, content, mime_type)},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


def load_sessions() -> list[dict]:
    return api_get("/sessions")


def load_session_messages(session_id: int) -> list[dict]:
    return api_get(f"/sessions/{session_id}/messages")


def create_session(title: str) -> dict:
    return api_post("/sessions", {"title": title})


def send_message(message: str, session_id: int | None, use_rag: bool) -> dict:
    return api_post(
        "/chat",
        {
            "message": message,
            "session_id": session_id,
            "use_rag": use_rag,
        },
    )


def index_documents() -> dict:
    return api_post("/rag/index")


def upload_document(filename: str, content: bytes, mime_type: str) -> dict:
    return api_upload("/rag/upload", filename, content, mime_type)


def init_state() -> None:
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None

    if "use_rag" not in st.session_state:
        st.session_state.use_rag = False

    if "sessions_cache" not in st.session_state:
        st.session_state.sessions_cache = []

    if "last_error" not in st.session_state:
        st.session_state.last_error = None


def refresh_sessions() -> None:
    try:
        st.session_state.sessions_cache = load_sessions()
        st.session_state.last_error = None
    except Exception as exc:
        st.session_state.last_error = str(exc)


def render_sidebar() -> None:
    st.sidebar.title("My Local GPT")

    if st.sidebar.button("Обновить список чатов", use_container_width=True):
        refresh_sessions()

    st.session_state.use_rag = st.sidebar.toggle(
        "Использовать RAG",
        value=st.session_state.use_rag,
    )

    st.sidebar.divider()

    new_title = st.sidebar.text_input("Название нового чата", value="New chat")
    if st.sidebar.button("Создать чат", use_container_width=True):
        try:
            session = create_session(new_title.strip() or "New chat")
            st.session_state.current_session_id = session["session_id"]
            refresh_sessions()
            st.rerun()
        except Exception as exc:
            st.session_state.last_error = str(exc)

    st.sidebar.divider()
    st.sidebar.subheader("Документы")

    uploaded_file = st.sidebar.file_uploader(
        "Загрузить .txt или .md",
        type=["txt", "md"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        if st.sidebar.button("Сохранить файл", use_container_width=True):
            try:
                result = upload_document(
                    filename=uploaded_file.name,
                    content=uploaded_file.getvalue(),
                    mime_type=uploaded_file.type or "text/plain",
                )
                st.sidebar.success(
                    f"Файл загружен: {result['filename']} ({result['size']} байт)"
                )
            except Exception as exc:
                st.session_state.last_error = str(exc)

    if st.sidebar.button("Переиндексировать документы", use_container_width=True):
        try:
            result = index_documents()
            st.sidebar.success(
                f"Файлов: {result['files_indexed']}, чанков: {result['chunks_indexed']}"
            )
        except Exception as exc:
            st.session_state.last_error = str(exc)

    st.sidebar.divider()
    st.sidebar.subheader("Сессии")

    sessions = st.session_state.sessions_cache
    if not sessions:
        st.sidebar.caption("Сессий пока нет")
        return

    for session in sessions:
        title = session["title"]
        summary = session.get("summary")
        session_id = session["session_id"]

        label = f"#{session_id} · {title}"
        if st.sidebar.button(label, key=f"session_{session_id}", use_container_width=True):
            st.session_state.current_session_id = session_id
            st.rerun()

        if summary:
            st.sidebar.caption(summary[:120] + ("..." if len(summary) > 120 else ""))


def render_header() -> None:
    st.title("Локальный AI-ассистент")
    st.caption("FastAPI + Ollama + SQLite + RAG")

    if st.session_state.current_session_id is None:
        st.info("Создай новый чат слева или отправь сообщение — сессия создастся автоматически.")
    else:
        st.success(f"Текущая сессия: {st.session_state.current_session_id}")

    if st.session_state.use_rag:
        st.caption("RAG включён: ответы могут опираться на проиндексированные документы.")


def render_messages() -> None:
    session_id = st.session_state.current_session_id
    if session_id is None:
        return

    try:
        messages = load_session_messages(session_id)
    except Exception as exc:
        st.error(f"Не удалось загрузить сообщения: {exc}")
        return

    if not messages:
        st.caption("Сообщений пока нет.")
        return

    for message in messages:
        role = message["role"]
        content = message["content"]

        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(content)


def render_input() -> None:
    prompt = st.chat_input("Напиши сообщение")
    if not prompt:
        return

    session_id = st.session_state.current_session_id

    try:
        with st.spinner("Модель думает..."):
            result = send_message(
                message=prompt,
                session_id=session_id,
                use_rag=st.session_state.use_rag,
            )

        st.session_state.current_session_id = result["session_id"]
        refresh_sessions()
        st.rerun()
    except Exception as exc:
        st.error(f"Ошибка отправки сообщения: {exc}")


def main() -> None:
    st.set_page_config(page_title="My Local GPT", page_icon="🤖", layout="wide")
    init_state()

    if not st.session_state.sessions_cache:
        refresh_sessions()

    render_sidebar()
    render_header()

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    render_messages()
    render_input()


if __name__ == "__main__":
    main()