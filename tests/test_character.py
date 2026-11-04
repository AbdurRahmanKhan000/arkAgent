"""Character tests: GUI state machine, without needing a display."""
import unittest

from ark_agent.character import STATES, next_frame, state_message


class TestCharacter(unittest.TestCase):
    def test_all_states_have_messages(self):
        for state in STATES:
            with self.subTest(state=state):
                self.assertTrue(state_message(state))

    def test_speaking_mouth_animates(self):
        frames = [next_frame("speaking", tick) for tick in range(4)]
        mouths = [f.mouth_open for f in frames]
        self.assertIn(True, mouths)
        self.assertIn(False, mouths)

    def test_working_gear_turns(self):
        angles = [next_frame("working", tick).gear_angle for tick in range(4)]
        self.assertEqual(len(set(angles)), 4)

    def test_idle_does_not_talk_or_work(self):
        frame = next_frame("idle", 1)
        self.assertFalse(frame.mouth_open)
        self.assertEqual(frame.gear_angle, 0)
        self.assertFalse(frame.ears_up)

    def test_listening_ears_up(self):
        self.assertTrue(next_frame("listening", 1).ears_up)

    def test_unknown_state_falls_back_to_idle(self):
        frame = next_frame("dancing", 1)
        self.assertFalse(frame.mouth_open)
        self.assertEqual(frame.gear_angle, 0)


if __name__ == "__main__":
    unittest.main()
