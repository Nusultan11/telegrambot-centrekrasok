from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.prompts.assistant_prompt import build_system_prompt  # noqa: E402
from company_bot.assistant import CompanyAssistant  # noqa: E402
from company_bot.knowledge import KnowledgeBase  # noqa: E402
from company_bot.memory import DialogMemory  # noqa: E402
from company_bot.providers import AIProviderError, ChatProvider, Message  # noqa: E402


class RecordingProvider(ChatProvider):
    def __init__(self) -> None:
        self.messages: list[Message] = []

    async def generate(self, messages: list[Message]) -> str:
        self.messages = messages
        return "Ответ по компании"


class FailingProvider(ChatProvider):
    async def generate(self, messages: list[Message]) -> str:
        raise AIProviderError("forced failure")


class CompanyAssistantTest(unittest.IsolatedAsyncioTestCase):
    async def test_prompt_layer_contains_guardrails(self) -> None:
        prompt = build_system_prompt()

        self.assertIn("Используй только переданный контекст", prompt)
        self.assertIn("Не придумывай цены", prompt)
        self.assertIn("Если в контексте нет точной информации", prompt)
        self.assertIn("Не упоминай внутренние слова", prompt)

    async def test_prompt_contains_company_rules_and_context(self) -> None:
        provider = RecordingProvider()
        assistant = CompanyAssistant(
            knowledge_base=KnowledgeBase.from_markdown(
                ROOT / "data" / "company_profile.md"
            ),
            provider=provider,
            memory=DialogMemory(max_messages=4),
            top_k_chunks=3,
            provider_name="test",
        )

        answer = await assistant.answer(1, "Какие услуги предоставляет компания?")

        self.assertEqual(answer.text, "Ответ по компании")
        joined = "\n".join(message["content"] for message in provider.messages)
        self.assertIn("Не придумывай цены", joined)
        self.assertIn("Отвечай развернуто", joined)
        self.assertIn("3-6 содержательных", joined)
        self.assertNotIn("Markdown", joined)
        self.assertIn("Контекст компании:", joined)
        self.assertIn("Услуги", joined)

    async def test_memory_keeps_dialog_context(self) -> None:
        provider = RecordingProvider()
        memory = DialogMemory(max_messages=4)
        assistant = CompanyAssistant(
            knowledge_base=KnowledgeBase.from_markdown(
                ROOT / "data" / "company_profile.md"
            ),
            provider=provider,
            memory=memory,
            top_k_chunks=2,
            provider_name="test",
        )

        await assistant.answer(42, "Где офис?")
        await assistant.answer(42, "А телефон?")

        roles = [message["role"] for message in provider.messages]
        self.assertIn("assistant", roles)
        self.assertEqual(memory.get(42)[-1]["content"], "Ответ по компании")

    async def test_clients_fallback_is_polished(self) -> None:
        assistant = CompanyAssistant(
            knowledge_base=KnowledgeBase.from_markdown(
                ROOT / "data" / "company_profile.md"
            ),
            provider=FailingProvider(),
            memory=DialogMemory(max_messages=4),
            top_k_chunks=3,
            provider_name="test",
        )

        answer = await assistant.answer(5, "Кто клиенты компании?")

        self.assertIn('Компания "Центр Красок #1"', answer.text)
        self.assertIn("• Частных клиентов:", answer.text)
        self.assertIn("• Дизайнеров:", answer.text)
        self.assertIn("• Строителей:", answer.text)
        self.assertIn("• Проектных заказчиков:", answer.text)
        self.assertNotIn("По данным компании:", answer.text)
        self.assertNotIn("нужно озвучивать аккуратно", answer.text)

    async def test_fallback_hides_internal_knowledge_labels(self) -> None:
        assistant = CompanyAssistant(
            knowledge_base=KnowledgeBase.from_markdown(
                ROOT / "data" / "company_profile.md"
            ),
            provider=FailingProvider(),
            memory=DialogMemory(max_messages=4),
            top_k_chunks=3,
            provider_name="test",
        )

        answer = await assistant.answer(6, "Чем занимается компания?")

        self.assertIn("Центр Красок #1", answer.text)
        self.assertNotIn("Known facts", answer.text)
        self.assertNotIn("Answering rules", answer.text)
        self.assertNotIn("Нельзя утверждать", answer.text)


if __name__ == "__main__":
    unittest.main()
