from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_bot.knowledge import KnowledgeBase, tokenize  # noqa: E402


class KnowledgeBaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.kb = KnowledgeBase.from_markdown(ROOT / "data" / "company_profile.md")

    def test_tokenize_supports_russian_text(self) -> None:
        self.assertIn("алматы", tokenize("Где офис в Алматы?"))

    def test_search_contacts(self) -> None:
        chunks = self.kb.search("где находится офис и какой телефон", top_k=3)
        text = "\n".join(chunk.text for chunk in chunks)
        self.assertIn("Кабдолова", text)
        self.assertIn("+7 778 061 5000", text)

    def test_search_vacancies(self) -> None:
        chunks = self.kb.search("какие есть вакансии", top_k=2)
        text = "\n".join(chunk.text for chunk in chunks)
        self.assertIn("не найден", text.lower())


if __name__ == "__main__":
    unittest.main()
