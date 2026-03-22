from typing import Dict, List

from app.core.config import settings
from app.llm.base import LLMProvider


SUMMARY_SYSTEM_PROMPT = (
    "Ты сервис суммаризации диалога. "
    "Сожми старую часть переписки в короткое полезное резюме. "
    "Сохраняй только важные факты, цели пользователя, принятые решения, "
    "ограничения, предпочтения и открытые вопросы. "
    "Не добавляй ничего от себя. "
    "Пиши кратко и структурно на русском языке."
)


class SummarizerService:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def should_update_summary(self, messages: List[Dict[str, str]]) -> bool:
        return len(messages) >= settings.summary_trigger_messages

    def split_messages_for_summary(
        self,
        messages: List[Dict[str, str]],
    ) -> tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        keep_count = settings.summary_keep_recent_messages

        if len(messages) <= keep_count:
            return [], messages

        old_messages = messages[:-keep_count]
        recent_messages = messages[-keep_count:]
        return old_messages, recent_messages

    def build_summary_request(
        self,
        existing_summary: str | None,
        old_messages: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        parts: list[str] = []

        if existing_summary:
            parts.append("Текущее summary диалога:")
            parts.append(existing_summary.strip())
            parts.append("")

        parts.append("Старые сообщения для обновления summary:")
        for msg in old_messages:
            role = "Пользователь" if msg["role"] == "user" else "Ассистент"
            parts.append(f"{role}: {msg['content']}")

        parts.append("")
        parts.append(
            "Обнови summary так, чтобы оно осталось коротким, полезным и не длиннее "
            f"{settings.summary_max_chars} символов."
        )

        return [{"role": "user", "content": "\n".join(parts)}]

    def update_summary(
        self,
        existing_summary: str | None,
        full_history: List[Dict[str, str]],
    ) -> tuple[str | None, List[Dict[str, str]]]:
        if not self.should_update_summary(full_history):
            return existing_summary, full_history

        old_messages, recent_messages = self.split_messages_for_summary(full_history)

        if not old_messages:
            return existing_summary, recent_messages

        summary_request = self.build_summary_request(
            existing_summary=existing_summary,
            old_messages=old_messages,
        )

        new_summary = self.provider.generate(
            system_prompt=SUMMARY_SYSTEM_PROMPT,
            messages=summary_request,
        ).strip()

        if len(new_summary) > settings.summary_max_chars:
            new_summary = new_summary[: settings.summary_max_chars].rstrip()

        return new_summary, recent_messages