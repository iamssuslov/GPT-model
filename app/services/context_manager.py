from typing import List, Dict


class ContextManager:
    def __init__(self, max_chars: int, max_messages: int):
        self.max_chars = max_chars
        self.max_messages = max_messages

    @staticmethod
    def _message_size(message: Dict[str, str]) -> int:
        return len(message.get("content", ""))

    def build_context(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Берёт последние max_messages сообщений и дополнительно
        ограничивает итоговый контекст по суммарному числу символов.
        """
        recent_messages = messages[-self.max_messages:]

        selected: List[Dict[str, str]] = []
        total_chars = 0

        for message in reversed(recent_messages):
            message_size = self._message_size(message)

            if selected and total_chars + message_size > self.max_chars:
                break

            if not selected and message_size > self.max_chars:
                truncated_message = {
                    "role": message["role"],
                    "content": message["content"][-self.max_chars:],
                }
                selected.append(truncated_message)
                total_chars = len(truncated_message["content"])
                break

            selected.append(message)
            total_chars += message_size

        selected.reverse()
        return selected