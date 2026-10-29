import gc
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication

from database.db_manager import DBManager
from views.main_window import MainWindow


class UnsavedChangesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        db = DBManager(str(Path(self.folder.name) / "test.db"))
        db.init_db()
        self.window = MainWindow(db)
        self.window.tabs.setCurrentIndex(1)

    def tearDown(self):
        self.window.score_tab._modified.clear()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        gc.collect()
        self.folder.cleanup()

    def test_cancelled_tab_move_restores_score_tab(self):
        self.window.score_tab._modified[(1, 1, 1)] = {"korean": "70"}
        with patch.object(self.window.score_tab, "confirm_unsaved_changes", return_value=False) as confirm:
            self.window.tabs.setCurrentIndex(0)
            confirm.assert_not_called()
            self.app.processEvents()
            confirm.assert_called_once_with("탭 이동")
        self.assertEqual(self.window.tabs.currentIndex(), 1)

    def test_confirmed_tab_move_leaves_score_tab(self):
        self.window.score_tab._modified[(1, 1, 1)] = {"korean": "70"}
        with patch.object(self.window.score_tab, "confirm_unsaved_changes", return_value=True):
            self.window.tabs.setCurrentIndex(2)
            self.app.processEvents()
        self.assertEqual(self.window.tabs.currentIndex(), 2)

    def test_student_tab_updates_only_the_saved_student_row(self):
        self.window.db.update_scores(1, 1, 1, 70, 55, 73)
        self.window.student_tab.apply_score_updates([(1, 1, 1)])
        self.assertEqual(self.window.student_tab.table.item(0, 4).text(), "70")

    def test_close_event_is_ignored_when_unsaved_confirmation_is_cancelled(self):
        self.window.score_tab._modified[(1, 1, 1)] = {"korean": "70"}
        event = QCloseEvent()
        with patch.object(self.window.score_tab, "confirm_unsaved_changes", return_value=False):
            self.window.closeEvent(event)
        self.assertFalse(event.isAccepted())

    def test_close_event_is_accepted_when_unsaved_confirmation_is_confirmed(self):
        self.window.score_tab._modified[(1, 1, 1)] = {"korean": "70"}
        event = QCloseEvent()
        with patch.object(self.window.score_tab, "confirm_unsaved_changes", return_value=True):
            self.window.closeEvent(event)
        self.assertTrue(event.isAccepted())


if __name__ == "__main__":
    unittest.main()
