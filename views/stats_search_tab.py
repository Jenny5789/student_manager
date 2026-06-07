from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QComboBox, QLabel, QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ScoreSearchTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        grp = QGroupBox()
        row = QHBoxLayout(grp)
        row.setSpacing(8)

        self.ws_grade = QComboBox()
        self.ws_grade.setFixedWidth(110)
        self.ws_grade.addItem("전체", 0)
        for g in range(1, 4):
            self.ws_grade.addItem(f"{g}학년", g)

        self.ws_class = QComboBox()
        self.ws_class.setFixedWidth(100)
        self.ws_class.addItem("전체", 0)
        for c in range(1, 9):
            self.ws_class.addItem(f"{c}반", c)

        self.ws_subject = QComboBox()
        self.ws_subject.setFixedWidth(100)
        self.ws_subject.addItems(["국어", "영어", "수학", "평균"])

        self.ws_score = QLineEdit()
        self.ws_score.setText("60")
        self.ws_score.setFixedWidth(80)

        self.ws_condition = QComboBox()
        self.ws_condition.setFixedWidth(90)
        self.ws_condition.addItems(["이하", "이상"])

        btn = QPushButton("검색")
        btn.clicked.connect(self._search_score)

        row.addWidget(self.ws_grade)
        row.addWidget(self.ws_class)
        row.addWidget(self.ws_subject)
        row.addWidget(self.ws_score)
        row.addWidget(self.ws_condition)
        row.addWidget(btn)
        row.addStretch()
        layout.addWidget(grp)

        self.ws_table = QTableWidget()
        self.ws_table.setColumnCount(7)
        self.ws_table.setHorizontalHeaderLabels(
            ["학년", "반", "번호", "이름", "국어", "영어", "수학"]
        )
        self.ws_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section {"
            "  background-color: #b0bec5; color: #1a1a2e;"
            "  font-weight: 500; padding: 4px; border: none;"
            "  border-right: 0.5px solid #90a4ae;"
            "  border-bottom: 1px solid #78909c;"
            "}"
        )
        hdr = self.ws_table.horizontalHeader()
        for c in [0, 1, 2]:
            hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed)
        self.ws_table.setColumnWidth(3, 200)
        for c in [4, 5, 6]:
            hdr.setSectionResizeMode(c, QHeaderView.Fixed)
            self.ws_table.setColumnWidth(c, 100)
        self.ws_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ws_table.setAlternatingRowColors(True)
        self.ws_table.verticalHeader().setVisible(False)

        self.ws_lbl = QLabel("총 0명")
        self.ws_lbl.setObjectName("countLabel")

        layout.addWidget(self.ws_table, 1)
        layout.addWidget(self.ws_lbl)

    def _search_score(self):
        grade     = self.ws_grade.currentData()
        class_num = self.ws_class.currentData()
        subject   = self.ws_subject.currentText()
        try:
            threshold = int(self.ws_score.text())
        except ValueError:
            threshold = 60

        col_map = {"국어": "korean", "영어": "english", "수학": "math", "평균": "average"}
        col = col_map[subject]

        if grade and class_num:
            students = self.db.get_students_by_class(grade, class_num)
        elif grade:
            students = self.db.get_students_by_grade(grade)
        else:
            students = self.db.get_all_students()

        col_idx   = {"korean": 4, "english": 5, "math": 6, "average": 7}[col]
        condition = self.ws_condition.currentText()
        if condition == "이하":
            filtered = [s for s in students if s[col_idx] <= threshold]
        else:
            filtered = [s for s in students if s[col_idx] >= threshold]

        self.ws_table.setRowCount(len(filtered))
        for r, s in enumerate(filtered):
            for c, val in enumerate(s[:7]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                if c == col_idx and col_idx < 7:
                    item.setForeground(QColor("#ef4444"))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.ws_table.setItem(r, c, item)

        self.ws_lbl.setText(f"총 {len(filtered)}명")