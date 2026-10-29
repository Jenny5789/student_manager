from PyQt5.QtWidgets import (
    QComboBox, QListView, QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

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
        self._apply_combo_popup_fonts()

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
        self.score_tab.scores_saved.connect(self.student_tab.apply_score_updates)

        self.tabs.addTab(self.student_tab, "👤  학생 관리")
        self.tabs.addTab(self.score_tab,   "📝  성적 관리")
        self.tabs.addTab(self.stats_tab,   "📊  통계 & 시각화")
        self._active_tab_index = self.tabs.currentIndex()
        self._restoring_tab = False
        self._allow_tab_change = False
        self._pending_tab_index = None
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs)

    def _on_tab_changed(self, idx):
        if self._restoring_tab:
            return

        if self._allow_tab_change:
            self._allow_tab_change = False
        elif (self._active_tab_index == 1 and idx != 1
              and self.score_tab.has_unsaved_changes()):
            # QTabWidget의 currentChanged 신호 안에서 모달 창을 열면 Windows가
            # 잠시 응답 없음으로 판단할 수 있어, 먼저 탭을 되돌린 뒤 다음 이벤트에서 묻는다.
            self._restoring_tab = True
            self.tabs.setCurrentIndex(self._active_tab_index)
            self._restoring_tab = False
            self._pending_tab_index = idx
            QTimer.singleShot(0, self._confirm_tab_change)
            return

        self._active_tab_index = idx
        # 통계 탭으로 전환 시 자동 갱신
        if idx == 2:
            self.stats_tab.refresh()

    def _confirm_tab_change(self):
        target_index = self._pending_tab_index
        self._pending_tab_index = None
        if target_index is None:
            return
        if self.score_tab.confirm_unsaved_changes("탭 이동"):
            self._allow_tab_change = True
            self.tabs.setCurrentIndex(target_index)

    def closeEvent(self, event):
        if self.score_tab.confirm_unsaved_changes("종료"):
            event.accept()
        else:
            event.ignore()

    def _apply_combo_popup_fonts(self):
        """Windows 기본 팝업 대신 글꼴과 높이가 고정된 목록을 사용한다."""
        for combo in self.findChildren(QComboBox):
            view = QListView(combo)
            view.setFont(QFont("Malgun Gothic", 12))
            view.setStyleSheet("""
                QListView {
                    font: 12pt "Malgun Gothic";
                    background: #ffffff;
                    border: 1px solid #d0d7de;
                    outline: none;
                }
                QListView::item {
                    min-height: 32px;
                    padding: 4px 10px;
                }
                QListView::item:selected {
                    background: #dbeafe;
                    color: #0969da;
                }
            """)
            combo.setView(view)
            combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            combo.setMaxVisibleItems(4)

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
                    font-size: 13px;
                    padding: 6px 10px;
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
