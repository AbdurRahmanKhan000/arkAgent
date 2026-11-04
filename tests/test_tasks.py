"""Task planner tests: multi-step goals, not just single actions."""
import unittest

from ark_agent.tasks import TaskPlanner


class TestTasks(unittest.TestCase):
    def setUp(self):
        self.planner = TaskPlanner()

    def test_chrome_search_task(self):
        plan = self.planner.plan("open chrome and search for cats")
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual(plan.steps, ["open chrome", "search for cats"])

    def test_word_document_task(self):
        plan = self.planner.plan("create a word document and type hello world")
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertIn("open microsoft word", plan.steps)
        self.assertIn("type hello world and press enter", plan.steps)

    def test_work_setup_task(self):
        plan = self.planner.plan("set up my work")
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual(len(plan.steps), 3)

    def test_multi_command_fallback_is_a_task(self):
        plan = self.planner.plan("open chrome and open notepad")
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual(plan.steps, ["open chrome", "open notepad"])

    def test_single_command_is_not_a_task(self):
        self.assertIsNone(self.planner.plan("open chrome"))

    def test_unknown_sentence_is_not_a_task(self):
        self.assertIsNone(self.planner.plan("do something impossible right now"))

    def test_task_steps_resolve_to_commands(self):
        plan = self.planner.plan("open chrome and search for cats")
        assert plan is not None
        commands = self.planner.plan_to_commands(plan)
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0].action, "launch_app")
        self.assertEqual(commands[1].action, "search_text")


if __name__ == "__main__":
    unittest.main()
