from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget
from PyQt5.QtCore import Qt

from views.student_tab import StudentTab
from views.score_tab import ScoreTab
from views.stats_tab import StatsTab


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("학생 성적 관리 시스템")
        self.setMinimumSize(1100, 720)
        self._build_ui()
        self._apply_styles()

    # ── UI 구성 ──────────────────────────────────────────────
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # 헤더
        header = QLabel("📚  학생 성적 관리 시스템")
        header.setAlignment(Qt.AlignCenter)
        header.setObjectName("appTitle")
        layout.addWidget(header)

        # 탭
        self.tabs = QTabWidget()
        self.student_tab = StudentTab(self.db)
        self.score_tab   = ScoreTab(self.db)
        self.stats_tab   = StatsTab(self.db)

        self.tabs.addTab(self.student_tab, "👤  학생 관리")
        self.tabs.addTab(self.score_tab,   "📝  성적 관리")
        self.tabs.addTab(self.stats_tab,   "📊  통계 & 시각화")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs)

    def _on_tab_changed(self, idx):
        # 통계 탭으로 전환 시 자동 갱신
        if idx == 2:
            self.stats_tab.refresh()

    # ── 전역 스타일시트 ──────────────────────────────────────
    def _apply_styles(self):
            self.setStyleSheet("""
                /* ── 전체 배경 ── */
                QMainWindow, QWidget {
                    background-color: #f0f2f5;
                    font-family: "Apple SD Gothic Neo", "맑은 고딕", "Malgun Gothic", sans-serif;
                }

                /* ── 앱 타이틀 ── */
                #appTitle {
                    font-size: 22px;
                    font-weight: bold;
                    color: #1e3a5f;
                    padding: 8px 0;
                    letter-spacing: 1px;
                }

                /* ── 탭 ── */
                QTabWidget::pane {
                    background: #ffffff;
                    border: 1px solid #d0d7de;
                    border-radius: 10px;
                }
                QTabBar::tab {
                    background: #dfe4ea;
                    color: #57606a;
                    padding: 10px 24px;
                    margin-right: 4px;
                    border-radius: 8px 8px 0 0;
                    font-size: 13px;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                    color: #0969da;
                }
                QTabBar::tab:hover:!selected {
                    background: #c8cfd8;
                }

                /* ── 그룹박스 ── */
                QGroupBox {
                    background: #ffffff;
                    border: 1px solid #d0d7de;
                    border-radius: 8px;
                    margin-top: 14px;
                    padding: 10px 12px 12px 12px;
                    font-size: 13px;
                    font-weight: bold;
                    color: #24292f;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px;
                    color: #0969da;
                }

                /* ── 버튼 ── */
                QPushButton {
                    background-color: #0969da;
                    color: #ffffff;
                    border: none;
                    padding: 7px 18px;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover  { background-color: #0550ae; }
                QPushButton:pressed{ background-color: #033d8b; }

                QPushButton#btnDanger  { background-color: #cf222e; }
                QPushButton#btnDanger:hover  { background-color: #a40e26; }

                QPushButton#btnSuccess { background-color: #1a7f37; }
                QPushButton#btnSuccess:hover { background-color: #14612b; }

                QPushButton#btnNeutral { background-color: #6e7781; }
                QPushButton#btnNeutral:hover { background-color: #57606a; }

                /* ── 입력 위젯 ── */
                QLineEdit {
                    background: #ffffff;
                    border: 1px solid #d0d7de;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-size: 13px;
                    color: #24292f;
                }
                QSpinBox {
                    background: #ffffff;
                    border: 1px solid #d0d7de;
                    border-radius: 6px;
                    padding: 6px 24px 6px 10px;
                    font-size: 13px;
                    color: #24292f;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 0px;
                    height: 0px;
                    border: none;
                }
                QComboBox {
                    background: #ffffff;
                    border: 1px solid #d0d7de;
                    border-radius: 6px;
                    padding: 6px 24px 6px 10px;
                    font-size: 13px;
                    color: #24292f;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                    border: 1.5px solid #0969da;
                }
                QComboBox QAbstractItemView {
                    background: #ffffff;
                    border: 1px solid #d0d7de;
                    selection-background-color: #dbeafe;
                    selection-color: #0969da;
                }

                /* ── 테이블 ── */
                QTableWidget {
                    background: #ffffff;
                    border: 1px solid #d0d7de;
                    border-radius: 8px;
                    gridline-color: #eaeef2;
                    font-size: 13px;
                    color: #24292f;
                }
                QTableWidget::item { padding: 4px 8px; }
                QTableWidget::item:selected {
                    background: #dbeafe;
                    color: #0969da;
                }
                QTableWidget::item:alternate { background: #f6f8fa; }
                QHeaderView::section {
                    background-color: #1e3a5f;
                    color: #ffffff;
                    padding: 8px 10px;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                    border-right: 1px solid #2d5180;
                }

                /* ── 레이블 ── */
                QLabel#sectionLabel {
                    font-size: 13px;
                    color: #57606a;
                    font-weight: bold;
                }
                QLabel#countLabel {
                    font-size: 13px;
                    color: #57606a;
                }

                /* ── 스크롤바 ── */
                QScrollBar:vertical {
                    width: 8px;
                    background: #f6f8fa;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: #c8cfd8;
                    border-radius: 4px;
                    min-height: 24px;
                }
            """)