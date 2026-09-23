import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals/support"))
from app import route_ticket


class IntegrationTests(unittest.TestCase):
    def test_existing_path_and_semantic_path(self):
        self.assertEqual(route_ticket("refund please"), "billing")
        self.assertEqual(route_ticket("二重に引き落とされた", lambda _: {"choice": "billing", "confidence": .97}), "billing")

    def test_uncertainty_invalid_and_service_failure(self):
        for answer in ({"choice": "billing", "confidence": .5}, {"choice": "delete", "confidence": 1}, {"choice": "billing", "confidence": True}, {}):
            self.assertEqual(route_ticket("hello", lambda _, a=answer: a), "general")
        def unavailable(_):
            raise TimeoutError()
        self.assertEqual(route_ticket("refund", unavailable), "billing")


if __name__ == "__main__":
    unittest.main()
