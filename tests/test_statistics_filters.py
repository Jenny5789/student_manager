import gc
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication, QMessageBox

from database.db_manager import DBManager
from views.stats_ranking_tab import RankingTab
from views.stats_search_tab import ScoreSearchTab


class StatisticsFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db = DBManager(str(Path(self.folder.name) / "test.db"))
        self.db.init_db()
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM students")
            conn.executemany(
                "INSERT INTO students "
                "(grade,class_num,num,name,korean,english,math,average) "
                "VALUES (?,?,?,?,?,?,?,?)",
                [
                    (1, 1, 1, "A", 90, 80, 70, 80),
                    (1, 1, 2, "B", 60, 50, 40, 50),
                    (1, 2, 1, "C", 70, 70, 70, 70),
                    (2, 1, 1, "D", 20, 30, 40, 30),
                ],
            )
        self.ranking = RankingTab(self.db)
        self.search = ScoreSearchTab(self.db)
        self.info = patch.object(QMessageBox, "information", return_value=QMessageBox.Ok)
        self.warning = patch.object(QMessageBox, "warning", return_value=QMessageBox.Ok)
        self.info_mock = self.info.start()
        self.warning_mock = self.warning.start()

    def tearDown(self):
        self.info.stop()
        self.warning.stop()
        self.ranking.close()
        self.search.close()
        self.ranking.deleteLater()
        self.search.deleteLater()
        self.app.processEvents()
        gc.collect()
        self.folder.cleanup()

    def test_ranking_starts_without_loading_all_students(self):
        self.assertEqual(self.ranking.rk_table.rowCount(), 0)
        self.assertFalse(self.ranking.rk_class.isEnabled())

    def test_ranking_requires_grade_and_filters_class(self):
        self.ranking._update_ranking()
        self.info_mock.assert_called_once()
        self.ranking.rk_grade.setCurrentIndex(1)
        self.assertTrue(self.ranking.rk_class.isEnabled())
        self.ranking.rk_class.setCurrentIndex(1)
        self.ranking._update_ranking()
        self.assertEqual(self.ranking.rk_table.rowCount(), 2)
        self.assertEqual(self.ranking.rk_table.item(0, 4).text(), "A")
        self.assertEqual(self.ranking.rk_table.item(1, 4).text(), "B")

    def test_score_search_requires_grade_and_valid_threshold(self):
        self.search._search_score()
        self.info_mock.assert_called_once()
        self.search.ws_grade.setCurrentIndex(1)
        self.search.ws_score.setText("bad")
        self.search._search_score()
        self.warning_mock.assert_called_once()
        self.search.ws_score.setText("65")
        self.search.ws_condition.setCurrentIndex(1)
        self.search._search_score()
        self.assertEqual(self.search.ws_table.rowCount(), 2)


if __name__ == "__main__":
    unittest.main()
