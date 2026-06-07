from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from views.stats_class_tab import ClassCompareTab
from views.stats_search_tab import ScoreSearchTab
from views.stats_ranking_tab import RankingTab


class StatsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.inner_tabs = QTabWidget()
        self.class_tab   = ClassCompareTab(self.db)
        self.search_tab  = ScoreSearchTab(self.db)
        self.ranking_tab = RankingTab(self.db)

        self.inner_tabs.addTab(self.class_tab,   "📊  학급별 성적 비교")
        self.inner_tabs.addTab(self.search_tab,  "🔎  성적별 학생 조회")
        self.inner_tabs.addTab(self.ranking_tab, "🏆  성적 순위")
        layout.addWidget(self.inner_tabs)

    def refresh(self):
        self.class_tab.refresh()
        self.ranking_tab.refresh()