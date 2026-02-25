import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtWidgets import QApplication, QLabel

from visulite.models.app_state import DatasetMeta
from visulite.ui.main_window import MainWindow
from visulite.ui.surfaces import SurfaceFrame


class MainWindowSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._settings_dir = TemporaryDirectory()
        QSettings.setDefaultFormat(QSettings.IniFormat)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, cls._settings_dir.name)
        QCoreApplication.setOrganizationName("VisuLiteTests")
        QCoreApplication.setApplicationName("VisuLiteSmoke")
        cls._app = QApplication.instance() or QApplication([])

    @classmethod
    def tearDownClass(cls) -> None:
        cls._settings_dir.cleanup()

    def setUp(self) -> None:
        self.window = MainWindow()
        self.window.show()
        QApplication.processEvents()
        self.window._restore_balanced_view()
        QApplication.processEvents()

    def tearDown(self) -> None:
        self.window.close()
        QApplication.processEvents()

    def test_layout_toggle_actions_do_not_break_splitter_state(self) -> None:
        # Surface containers should exist.
        surfaces = self.window.findChildren(SurfaceFrame)
        self.assertTrue(any(s.property("surface") == "glass" for s in surfaces))
        self.assertTrue(any(s.property("surface") == "card" for s in surfaces))
        self.assertTrue(any(s.property("surface") == "panel" for s in surfaces))

        initial_sizes = self.window.main_splitter.sizes()
        self.window._toggle_sidebar()
        QApplication.processEvents()
        toggled_sizes = self.window.main_splitter.sizes()
        self.assertNotEqual(initial_sizes, toggled_sizes)

        self.window._toggle_sidebar()
        QApplication.processEvents()
        restored_sizes = self.window.main_splitter.sizes()
        self.assertNotEqual(toggled_sizes, restored_sizes)

        if self.window._chart_focus_mode:
            self.window._toggle_chart_focus()
            QApplication.processEvents()

        self.window._toggle_chart_focus()
        QApplication.processEvents()
        focus_sizes = self.window.content_splitter.sizes()
        self.assertTrue(self.window._chart_focus_mode)
        self.assertLessEqual(focus_sizes[0], 1)

        self.window._toggle_chart_focus()
        QApplication.processEvents()
        exit_focus_sizes = self.window.content_splitter.sizes()
        self.assertFalse(self.window._chart_focus_mode)
        self.assertNotEqual(focus_sizes, exit_focus_sizes)

    def test_sidebar_action_dock_and_form_labels(self) -> None:
        self.assertTrue(hasattr(self.window, "sidebar_scroll_area"))
        self.assertTrue(hasattr(self.window, "sidebar_action_dock"))
        self.assertTrue(hasattr(self.window, "sidebar_update_button"))
        self.assertTrue(hasattr(self.window, "sidebar_export_button"))

        dock = self.window.sidebar_action_dock
        scroll_area = self.window.sidebar_scroll_area
        scroll_content = scroll_area.widget()

        self.assertEqual(dock.objectName(), "sidebar-action-dock")
        self.assertIsNotNone(scroll_content)
        self.assertIsNone(scroll_content.findChild(type(dock), "sidebar-action-dock"))
        self.assertTrue(self.window.sidebar_update_button.isEnabled())
        self.assertTrue(self.window.sidebar_export_button.isEnabled())

        processing_labels = [
            label
            for label in self.window.findChildren(QLabel)
            if label.property("class") == "form-label" and label.text().strip()
        ]
        self.assertTrue(processing_labels)

        target = next(
            (
                label
                for label in processing_labels
                if "类型" in label.text() or "转换" in label.text()
            ),
            processing_labels[0],
        )
        required_width = target.fontMetrics().horizontalAdvance(target.text())
        self.assertTrue(target.wordWrap())
        self.assertGreaterEqual(target.minimumWidth(), 100)
        self.assertGreaterEqual(target.width(), min(required_width, target.minimumWidth()))

    def test_data_mutation_undo_redo_and_table_search_workflow(self) -> None:
        frame = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "city": ["Tokyo", "Paris", "Berlin"],
                "value": [10, 20, 30],
            }
        )
        meta = DatasetMeta(path=Path("sample.csv"), rows=3, columns=3)

        self.window.state.set_dataset(frame, meta)
        self.window.table_model.update_frame(frame)
        self.window._populate_columns(frame.columns.tolist())
        self.window._refresh_stats()
        QApplication.processEvents()

        self.assertEqual(self.window.table_model.rowCount(), 3)
        self.assertFalse(self.window.state.can_undo())
        self.assertFalse(self.window.state.can_redo())

        mutated = frame.iloc[:2].copy()
        self.window._apply_data_mutation(mutated, "slice applied")
        QApplication.processEvents()

        self.assertEqual(self.window.table_model.rowCount(), 2)
        self.assertTrue(self.window.state.can_undo())
        self.assertFalse(self.window.state.can_redo())

        self.window._undo_last_change()
        QApplication.processEvents()
        self.assertEqual(self.window.table_model.rowCount(), 3)
        self.assertTrue(self.window.state.can_redo())

        self.window._redo_last_change()
        QApplication.processEvents()
        self.assertEqual(self.window.table_model.rowCount(), 2)

        self.window.table_search_input.setText("not-found")
        QApplication.processEvents()
        self.assertEqual(self.window.proxy_model.rowCount(), 0)

        self.window.table_search_input.setText("")
        QApplication.processEvents()
        self.assertEqual(self.window.proxy_model.rowCount(), 2)

    def test_load_file_preprocess_undo_redo_and_update_chart(self) -> None:
        with TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "sample.csv"
            frame = pd.DataFrame(
                {
                    "id": [1, 2, 3],
                    "city": ["Tokyo", "Paris", "Berlin"],
                    "value": [10.0, float("nan"), 30.0],
                }
            )
            frame.to_csv(csv_path, index=False, encoding="utf-8")

            # Load via the real loader path (no file dialog).
            self.window._load_file(csv_path)
            QApplication.processEvents()

            self.assertTrue(self.window.state.has_data())
            self.assertEqual(self.window.table_model.rowCount(), 3)

            # Configure a safe chart config (numeric x/y) to avoid QMessageBox warnings.
            x_idx = self.window.x_combo.findText("id")
            self.assertGreaterEqual(x_idx, 0)
            self.window.x_combo.setCurrentIndex(x_idx)

            selected = False
            for i in range(self.window.y_list.count()):
                item = self.window.y_list.item(i)
                if item.text() == "value":
                    item.setSelected(True)
                    selected = True
                else:
                    item.setSelected(False)
            self.assertTrue(selected)

            chart_type_idx = self.window.chart_type_combo.findData("line")
            self.assertGreaterEqual(chart_type_idx, 0)
            self.window.chart_type_combo.setCurrentIndex(chart_type_idx)
            QApplication.processEvents()

            # Should not raise or show modal dialogs.
            self.window._on_update_chart()
            QApplication.processEvents()

            # Preprocess: slice to first 2 rows.
            self.window.head_n_spin.setValue(2)
            self.window._slice_data()
            QApplication.processEvents()
            self.assertEqual(self.window.table_model.rowCount(), 2)

            # Filter to the row that contains a missing value.
            filter_col_idx = self.window.filter_column_combo.findText("city")
            self.assertGreaterEqual(filter_col_idx, 0)
            self.window.filter_column_combo.setCurrentIndex(filter_col_idx)
            self.window.filter_text_input.setText("Paris")
            self.window._apply_filters()
            QApplication.processEvents()
            self.assertEqual(self.window.table_model.rowCount(), 1)
            self.assertEqual(self.window.state.data_frame["city"].iloc[0], "Paris")

            # Fill missing with zeros.
            fill_idx = self.window.fill_method_combo.findData("zero")
            self.assertGreaterEqual(fill_idx, 0)
            self.window.fill_method_combo.setCurrentIndex(fill_idx)
            self.window._fill_missing()
            QApplication.processEvents()
            self.assertEqual(float(self.window.state.data_frame["value"].iloc[0]), 0.0)

            # Undo/Redo should roundtrip.
            self.assertTrue(self.window.state.can_undo())
            self.window._undo_last_change()
            QApplication.processEvents()
            self.assertTrue(pd.isna(self.window.state.data_frame["value"].iloc[0]))

            self.window._redo_last_change()
            QApplication.processEvents()
            self.assertEqual(float(self.window.state.data_frame["value"].iloc[0]), 0.0)

            # Ensure chart update still works after mutations.
            self.window._on_update_chart()
            QApplication.processEvents()


if __name__ == "__main__":
    unittest.main()
