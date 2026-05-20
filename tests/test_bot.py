from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_bot.bot import format_telegram_html, strip_html  # noqa: E402


class TelegramFormattingTest(unittest.TestCase):
    def test_markdown_list_becomes_telegram_html(self) -> None:
        raw = (
            'Компания "Центр Красок #1" работает с разными клиентами:\n\n'
            "*   **Частных клиентов:** Люди для ремонта дома.\n"
            "*   **Дизайнеров:** Профессионалы с дизайн-проектами."
        )

        formatted = format_telegram_html(raw)

        self.assertIn("• <b>Частных клиентов:</b> Люди для ремонта дома.", formatted)
        self.assertIn("• <b>Дизайнеров:</b> Профессионалы", formatted)
        self.assertNotIn("*", formatted)

    def test_escapes_raw_html_but_keeps_bold_tags(self) -> None:
        formatted = format_telegram_html("<b>Бренды</b>: Paint & Paper <Library>")

        self.assertEqual(
            formatted,
            "<b>Бренды</b>: Paint &amp; Paper &lt;Library&gt;",
        )

    def test_strip_html_for_plain_fallback(self) -> None:
        self.assertEqual(strip_html("• <b>Адрес</b>: Алматы"), "• Адрес: Алматы")


if __name__ == "__main__":
    unittest.main()
