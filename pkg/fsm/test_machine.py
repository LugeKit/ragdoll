import unittest

from .machine import *


class TestMachine(unittest.TestCase):
    def test_init_next_state_not_exist(self):
        states = {
            State(
                name="state1",
                next_states={"state2"}
            )
        }

        with self.assertRaises(StateNotFound):
            _ = Machine(states, initial_state="state1")

    def test_init_initial_state_not_exist(self):
        states = {
            State(
                name="state1"
            )
        }

        with self.assertRaises(StateNotFound):
            _ = Machine(states, initial_state="state_not_exist")

    def test_init_successfully(self):
        states = {
            State(
                name="state1",
                next_states={
                    "state2"
                }
            ),
            State(
                name="state2",
                next_states={
                    "state1"
                }
            )
        }

        m = Machine(states, "state1")
        self.assertEqual("state1", m.state())

    @staticmethod
    def _create_test_machine() -> Machine:
        states = {
            State(
                name="state1",
                next_states={
                    "state2"
                }
            ),
            State(
                name="state2",
                next_states={
                    "state1",
                    "state3"
                }
            ),
            State(
                name="state3",
            )
        }
        return Machine(states, "state1")

    def test_trans_to_not_found(self):
        m = self._create_test_machine()
        with self.assertRaises(StateNotFound):
            m.trans_to("not_exist_state")

    def test_trans_to_illegal(self):
        m = self._create_test_machine()
        with self.assertRaises(StateTransIllegal):
            m.trans_to("state3")

    def test_trans_to_successfully(self):
        m = self._create_test_machine()
        self.assertEqual("state1", m.state())
        m.trans_to("state2")
        self.assertEqual("state2", m.state())
        m.trans_to("state3")
        self.assertEqual("state3", m.state())

    def test_trans_to_callback(self):
        count = 0

        def on_exit_s1(s1, s2):
            nonlocal count
            self.assertEqual(0, count)
            self.assertEqual("state1", s1)
            self.assertEqual("state2", s2)
            count += 1

        def on_enter_s2(s1, s2):
            self.assertEqual("state1", s1)
            self.assertEqual("state2", s2)
            self.assertEqual(1, count)

        states = {
            State(
                name="state1",
                next_states={"state2"},
                on_exit=on_exit_s1,
            ),
            State(
                name="state2",
                on_enter=on_enter_s2
            ),
        }
        m = Machine(states, "state1")
        m.trans_to("state2")
        self.assertEqual("state2", m.state())
