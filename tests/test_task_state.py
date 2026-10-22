import unittest

from lilyai.agent.state_machine import FINAL_STATES, IllegalTransition, StateMachine, TaskState as S


class StateMachineTests(unittest.TestCase):
    def test_happy_path(self):
        m = StateMachine()
        for s in (S.PLANNING, S.AWAITING_APPROVAL, S.RUNNING, S.VERIFYING, S.COMPLETED):
            m.transition(s)
        self.assertTrue(m.is_final)

    def test_illegal_transition_rejected(self):
        with self.assertRaises(IllegalTransition):
            StateMachine().transition(S.RUNNING)

    def test_same_state_transition_is_illegal(self):
        m = StateMachine()
        m.transition(S.PLANNING)
        with self.assertRaises(IllegalTransition):
            m.transition(S.PLANNING)

    def test_final_states_have_no_exits(self):
        for final in FINAL_STATES:
            m = StateMachine(final)
            for target in S:
                self.assertFalse(m.can_transition(target), (final, target))

    def test_every_active_state_can_be_cancelled(self):
        for s in (S.CREATED, S.PLANNING, S.AWAITING_APPROVAL, S.RUNNING, S.VERIFYING):
            self.assertTrue(StateMachine(s).can_transition(S.CANCELLED), s)
