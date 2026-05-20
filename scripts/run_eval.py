from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from company_bot.assistant import CompanyAssistant  # noqa: E402
from company_bot.knowledge import KnowledgeBase  # noqa: E402
from company_bot.memory import DialogMemory  # noqa: E402
from company_bot.providers import AIProviderError, ChatProvider, Message  # noqa: E402


class FailingProvider(ChatProvider):
    async def generate(self, messages: list[Message]) -> str:
        raise AIProviderError("eval uses local fallback only")


def load_eval_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    active_list: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- id:"):
            if current:
                cases.append(current)
            current = {"id": _yaml_value(stripped.removeprefix("- id:").strip())}
            active_list = None
            continue
        if current is None:
            continue
        if stripped.endswith(":"):
            active_list = stripped[:-1]
            current[active_list] = []
            continue
        if stripped.startswith("- ") and active_list:
            current[active_list].append(_yaml_value(stripped[2:].strip()))
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = _yaml_value(value.strip())
            active_list = None

    if current:
        cases.append(current)
    return cases


def _yaml_value(value: str) -> str:
    return value.strip().strip('"').strip("'")


async def run_eval(cases_path: Path) -> int:
    assistant = CompanyAssistant(
        knowledge_base=KnowledgeBase.from_markdown(ROOT / "data" / "company_profile.md"),
        provider=FailingProvider(),
        memory=DialogMemory(max_messages=4),
        top_k_chunks=3,
        provider_name="eval",
    )

    cases = load_eval_cases(cases_path)
    failures: list[str] = []

    for index, case in enumerate(cases, start=1):
        answer = await assistant.answer(index, str(case["question"]))
        text = answer.text
        missing = [
            item
            for item in case.get("must_contain", [])
            if item.lower() not in text.lower()
        ]
        forbidden = [
            item
            for item in case.get("must_not_contain", [])
            if item.lower() in text.lower()
        ]

        if missing or forbidden:
            failures.append(str(case["id"]))
            print(f"FAIL {case['id']}")
            if missing:
                print(f"  missing: {', '.join(missing)}")
            if forbidden:
                print(f"  forbidden: {', '.join(forbidden)}")
            print(f"  answer: {text}")
        else:
            print(f"PASS {case['id']}")

    print(f"\nResult: {len(cases) - len(failures)}/{len(cases)} passed")
    return 1 if failures else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local assistant evaluation cases.")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "eval" / "test_cases.yaml",
        help="Path to eval/test_cases.yaml",
    )
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run_eval(args.cases)))


if __name__ == "__main__":
    main()
