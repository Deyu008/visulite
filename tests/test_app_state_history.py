import unittest

import pandas as pd

from visulite.models.app_state import AppState, DatasetMeta


def _frame(value: int) -> pd.DataFrame:
    return pd.DataFrame({"value": [value]})


class AppStateHistoryTests(unittest.TestCase):
    def test_undo_and_redo_roundtrip(self) -> None:
        state = AppState()
        state.set_dataset(_frame(1), DatasetMeta(rows=1, columns=1))

        state.push_history(state.data_frame)
        state.update_view(_frame(2))
        state.push_history(state.data_frame)
        state.update_view(_frame(3))

        undo_one = state.undo()
        self.assertIsNotNone(undo_one)
        self.assertEqual(undo_one["value"].tolist(), [2])

        undo_two = state.undo()
        self.assertIsNotNone(undo_two)
        self.assertEqual(undo_two["value"].tolist(), [1])
        self.assertIsNone(state.undo())

        redo_one = state.redo()
        self.assertIsNotNone(redo_one)
        self.assertEqual(redo_one["value"].tolist(), [2])

        redo_two = state.redo()
        self.assertIsNotNone(redo_two)
        self.assertEqual(redo_two["value"].tolist(), [3])
        self.assertIsNone(state.redo())

    def test_push_history_clears_redo_stack(self) -> None:
        state = AppState()
        state.set_dataset(_frame(1), DatasetMeta(rows=1, columns=1))

        state.push_history(state.data_frame)
        state.update_view(_frame(2))
        state.push_history(state.data_frame)
        state.update_view(_frame(3))

        self.assertIsNotNone(state.undo())
        self.assertTrue(state.can_redo())

        state.push_history(state.data_frame)
        state.update_view(_frame(4))
        self.assertFalse(state.can_redo())

    def test_history_limit_is_enforced(self) -> None:
        state = AppState(history_limit=2)
        state.set_dataset(_frame(1), DatasetMeta(rows=1, columns=1))

        for next_value in (2, 3, 4):
            state.push_history(state.data_frame)
            state.update_view(_frame(next_value))

        self.assertEqual(state.undo()["value"].tolist(), [3])
        self.assertEqual(state.undo()["value"].tolist(), [2])
        self.assertIsNone(state.undo())

    def test_set_dataset_clears_history_and_uses_copies(self) -> None:
        state = AppState()
        source = _frame(1)
        state.set_dataset(source, DatasetMeta(rows=1, columns=1))

        source.iloc[0, 0] = 99
        self.assertEqual(state.data_frame["value"].tolist(), [1])
        self.assertEqual(state.original_frame["value"].tolist(), [1])

        state.push_history(state.data_frame)
        state.update_view(_frame(2))
        self.assertTrue(state.can_undo())

        state.set_dataset(_frame(10), DatasetMeta(rows=1, columns=1))
        self.assertFalse(state.can_undo())
        self.assertFalse(state.can_redo())
        self.assertEqual(state.data_frame["value"].tolist(), [10])


if __name__ == "__main__":
    unittest.main()
