import gc
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication, QMessageBox

from database.db_manager import DBManager
from views.score_tab import ScoreTab


class ScoreWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db = DBManager(str(Path(self.folder.name) / "test.db"))
        self.db.init_db()
        conn = self.db.get_connection()
        with conn:
            conn.execute("DELETE FROM students")
            conn.executemany(
                "INSERT INTO students "
                "(grade,class_num,num,name,korean,english,math,average) "
                "VALUES (1,1,?,?,?,60,60,?)",
                [(1, "Alpha", 9, 43), (2, "Beta", 80, 200 / 3)],
            )
        conn.close()
        self.tab = ScoreTab(self.db)
        self.warning = patch.object(QMessageBox, "warning", return_value=QMessageBox.Ok)
        self.info = patch.object(QMessageBox, "information", return_value=QMessageBox.Ok)
        self.warning_mock = self.warning.start()
        self.info_mock = self.info.start()

    def tearDown(self):
        self.warning.stop()
        self.info.stop()
        self.tab.close()
        self.tab.deleteLater()
        self.app.processEvents()
        gc.collect()
        self.folder.cleanup()

    def student(self, num):
        return self.db.get_student(1, 1, num)[0]

    def test_invalid_row_prevents_partial_save(self):
        self.tab.table.item(0, 4).setText("70")
        self.tab.table.item(1, 4).setText("101")
        self.tab._save_scores()
        self.assertEqual(self.student(1)[4], 9)
        self.assertEqual(self.student(2)[4], 80)
        self.assertEqual(len(self.tab._modified), 2)
        self.warning_mock.assert_called_once()
        self.info_mock.assert_not_called()

    def test_edit_survives_search_and_saves_hidden_student(self):
        self.tab.table.item(0, 4).setText("70")
        self.tab.search_input.setText("Beta")
        self.tab._search_by_name()
        self.tab._save_scores()
        self.assertEqual(self.student(1)[4], 70)
        self.assertFalse(self.tab._modified)
        self.tab._load_all()
        self.assertEqual(self.tab.table.item(0, 4).text(), "70")

    def test_reload_preserves_pending_edit_and_highlight(self):
        self.tab.table.item(0, 4).setText("70")
        self.tab._load_all()
        self.assertEqual(self.tab.table.item(0, 4).text(), "70")
        self.assertTrue(self.tab.table.item(0, 4).font().bold())
        self.assertEqual(self.student(1)[4], 9)

    def test_scores_sort_numerically(self):
        self.tab._on_header_clicked(4)
        self.assertEqual(self.tab.table.item(0, 4).text(), "9")
        self.tab._on_header_clicked(4)
        self.assertEqual(self.tab.table.item(0, 4).text(), "80")

    def test_deleted_student_rolls_back_entire_save(self):
        self.tab.table.item(0, 4).setText("70")
        self.tab.table.item(1, 4).setText("90")
        self.db.delete_student(1, 1, 2)
        self.tab._save_scores()
        self.assertEqual(self.student(1)[4], 9)
        self.assertEqual(len(self.tab._modified), 2)
        self.warning_mock.assert_called_once()
        self.info_mock.assert_not_called()

    def test_valid_save_persists_and_clears_highlight(self):
        self.tab.table.item(0, 4).setText("0")
        self.tab.table.item(0, 5).setText("100")
        self.tab._save_scores()
        reopened = DBManager(self.db.db_path).get_student(1, 1, 1)[0]
        self.assertEqual(reopened[4:7], (0, 100, 60))
        self.assertAlmostEqual(reopened[7], 160 / 3)
        self.assertFalse(self.tab._modified)
        self.assertFalse(self.tab.table.item(0, 4).font().bold())

    def test_invalid_inputs_remain_pending_until_corrected(self):
        for text in ("", "abc", "1.5", "-1", "101"):
            with self.subTest(text=text):
                self.tab.table.item(0, 4).setText(text)
                self.tab._save_scores()
                self.assertEqual(self.student(1)[4], 9)
                self.assertTrue(self.tab._modified)
                self.assertEqual(self.tab.table.item(0, 7).text(), "입력 확인")
        self.tab.table.item(0, 4).setText("70")
        self.tab._save_scores()
        self.assertEqual(self.student(1)[4], 70)
        self.assertFalse(self.tab._modified)

    def test_database_error_preserves_pending_changes(self):
        self.tab.table.item(0, 4).setText("70")
        with patch.object(self.db, "update_scores_batch",
                          side_effect=sqlite3.OperationalError("database is locked")):
            self.tab._save_scores()
        self.assertEqual(self.student(1)[4], 9)
        self.assertTrue(self.tab._modified)
        self.warning_mock.assert_called_once()
        self.info_mock.assert_not_called()

    def test_save_keeps_other_subjects_updated_elsewhere(self):
        self.tab.table.item(0, 4).setText("70")
        self.db.update_scores(1, 1, 1, 9, 90, 60)
        self.tab._save_scores()
        self.assertEqual(self.student(1)[4:7], (70, 90, 60))
        self.assertAlmostEqual(self.student(1)[7], 220 / 3)

    def test_note_saves_without_saving_pending_score(self):
        self.tab.table.item(0, 4).setText("70")
        self.tab.table.item(0, 8).setText("test note")
        self.assertEqual(self.student(1)[4], 9)
        self.assertEqual(self.student(1)[8], "test note")
        self.assertTrue(self.tab._modified)

    def test_sorted_edit_saves_correct_student(self):
        self.tab._on_header_clicked(4)
        self.tab._on_header_clicked(4)
        self.tab.table.item(0, 4).setText("75")
        self.tab._save_scores()
        self.assertEqual(self.student(1)[4], 9)
        self.assertEqual(self.student(2)[4], 75)

    def test_empty_save_does_not_write_database(self):
        with patch.object(self.db, "update_scores_batch") as save:
            self.tab._save_scores()
        save.assert_not_called()
        self.info_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
