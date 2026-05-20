from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.rag import KnowledgeBase as RagKnowledgeBase  # noqa: E402
from company_bot.knowledge import KnowledgeBase, tokenize  # noqa: E402


class KnowledgeBaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.kb = KnowledgeBase.from_markdown(ROOT / "data" / "company_profile.md")

    def test_tokenize_supports_russian_text(self) -> None:
        self.assertIn("алматы", tokenize("Где офис в Алматы?"))

    def test_app_rag_import_is_available(self) -> None:
        self.assertIs(RagKnowledgeBase, KnowledgeBase)

    def test_search_contacts(self) -> None:
        chunks = self.kb.search("где находится офис и какой телефон", top_k=3)
        text = "\n".join(chunk.text for chunk in chunks)
        self.assertIn("Кабдолова", text)
        self.assertIn("+7 778 061 5000", text)

    def test_retrieves_contacts_for_location_question(self) -> None:
        chunks = self.kb.search("Где вы находитесь?", top_k=3)
        titles = [chunk.title for chunk in chunks]
        self.assertTrue(any("Stores And Contacts" in title for title in titles))

    def test_retrieves_builders_for_contractors_question(self) -> None:
        chunks = self.kb.search("Что вы предлагаете строителям?", top_k=3)
        titles = [chunk.title for chunk in chunks]
        self.assertTrue(
            any("Builders And Contractors" in title for title in titles)
        )

    def test_retrieves_company_overview_for_business_question(self) -> None:
        chunks = self.kb.search("Чем занимается Центр Красок?", top_k=3)
        titles = [chunk.title for chunk in chunks]
        self.assertTrue(
            any(
                "Business Scope" in title or "Company Overview" in title
                for title in titles
            )
        )

    def test_retrieves_products_for_products_question(self) -> None:
        chunks = self.kb.search("Какие товары у вас есть?", top_k=3)
        titles = [chunk.title for chunk in chunks]
        self.assertTrue(any("Products" in title for title in titles))

    def test_retrieves_brands_for_brands_question(self) -> None:
        chunks = self.kb.search("Какие бренды представлены?", top_k=3)
        titles = [chunk.title for chunk in chunks]
        self.assertTrue(any("Brands" in title for title in titles))

    def test_retrieves_designers_for_designer_offer_question(self) -> None:
        chunks = self.kb.search("Что вы предлагаете дизайнерам?", top_k=3)
        titles = [chunk.title for chunk in chunks]
        self.assertTrue(any("For Designers" in title for title in titles))

    def test_retrieves_company_context_for_why_choose_question(self) -> None:
        chunks = self.kb.search(
            "Объясни коротко, почему стоит обратиться в Центр Красок?",
            top_k=3,
        )
        titles = [chunk.title for chunk in chunks]
        self.assertTrue(
            any(
                "Company Overview" in title
                or "Business Scope" in title
                or "Services" in title
                for title in titles
            )
        )

    def test_search_vacancies(self) -> None:
        chunks = self.kb.search("какие есть вакансии", top_k=2)
        text = "\n".join(chunk.text for chunk in chunks)
        self.assertIn("не найден", text.lower())


if __name__ == "__main__":
    unittest.main()
