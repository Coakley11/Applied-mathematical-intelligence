"""Music Coach AMI routing and solvers in Command Center."""

from __future__ import annotations

import unittest

from components.applied_math_problem_router import MUSIC_PRACTICE_PLAN, route_suite_question
from components.applied_math_solvers import solve_suite_question
from components.music_ami_intent import detect_music_send_intent, minutes_from_question


class TestMusicIntent(unittest.TestCase):
    def test_fifteen_minute_practice_question_is_practice_plan(self) -> None:
        q = "I have 15 minutes to practice this song. What should I do?"
        self.assertEqual(detect_music_send_intent(q, "practice"), "practice_plan")
        self.assertEqual(minutes_from_question(q), 15)

    def test_routing_hint_honored(self) -> None:
        q = "Help?"
        self.assertEqual(
            detect_music_send_intent(q, "practice", {"routing_hint": "chord_transition"}),
            "chord_transition",
        )


class TestMusicRouting(unittest.TestCase):
    def test_route_music_practice_plan(self) -> None:
        q = "I have 15 minutes to practice this song. What should I do?"
        ctx = {
            "source_app": "music",
            "workflow": "Music practice coach",
            "instrument": "Guitar",
            "song": "Wonderwall",
            "coach_page": "practice",
        }
        route = route_suite_question(q, source_app="music", context=ctx)
        self.assertEqual(route.problem_type_id, MUSIC_PRACTICE_PLAN)
        self.assertGreaterEqual(route.confidence, 0.9)
        self.assertNotEqual(route.problem_type_id, "generic_interactive")

    def test_solve_returns_practice_plan_not_rebalance(self) -> None:
        q = "I have 15 minutes to practice this song. What should I do?"
        ctx = {
            "source_app": "music",
            "workflow": "Music practice coach",
            "instrument": "Guitar",
            "song": "Wonderwall",
            "coach_page": "practice",
        }
        route, result = solve_suite_question(q, source_app="music", context=ctx)
        self.assertEqual(route.problem_type_id, MUSIC_PRACTICE_PLAN)
        self.assertIn("15-minute", result.short_answer)
        self.assertNotIn("Rebalance", result.short_answer)
        self.assertNotIn("drift", result.short_answer.lower())


if __name__ == "__main__":
    unittest.main()
