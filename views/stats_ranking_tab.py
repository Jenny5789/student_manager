from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QComboBox, QLabel, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class RankingTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()
        self._update_ranking()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        grp = QGroupBox()
        row = QHBoxLayout(grp)
        row.setSpacing(8)

        self.rk_grade = QComboBox()
        self.rk_grade.setFixedWidth(110)
        self.rk_grade.addItem("전체", 0)
        for g in range(1, 4):
            self.rk_grade.addItem(f"{g}학년", g)

        self.rk_class = QComboBox()
        self.rk_class.setFixedWidth(100)
        self.rk_class.addItem("전체", 0)
        for c in range(1, 9):
            self.rk_class.addItem(f"{c}반", c)

        self.rk_subject = QComboBox()
        self.rk_subject.setFixedWidth(110)
        self.rk_subject.addItems(["전체 평균", "국어", "영어", "수학"])

        self.rk_order = QComboBox()
        self.rk_order.setFixedWidth(110)
        self.rk_order.addItems(["내림차순", "오름차순"])

        btn = QPushButton("조회")
        btn.clicked.connect(self._update_ranking)

        row.addWidget(self.rk_grade)
        row.addWidget(self.rk_class)
        row.addWidget(self.rk_subject)
        row.addWidget(self.rk_order)
        row.addWidget(btn)
        row.addStretch()
        layout.addWidget(grp)

        self.rk_table = QTableWidget()
        self.rk_table.setColumnCount(9)
        self.rk_table.setHorizontalHeaderLabels(
            ["순위", "학년", "반", "번호", "이름", "국어", "영어", "수학", "평균"]
        )
        self.rk_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section {"
            "  background-color: #b0bec5; color: #1a1a2e;"
            "  font-weight: 500; padding: 4px; border: none;"
            "  border-right: 0.5px solid #90a4ae;"
            "  border-bottom: 1px solid #78909c;"
            "}"
        )
        hdr = self.rk_table.horizontalHeader()
        for c in [0, 1, 2, 3]:
            hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed)
        self.rk_table.setColumnWidth(4, 200)
        for c in [5, 6, 7, 8]:
            hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)

        self.rk_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rk_table.setAlternatingRowColors(True)
        self.rk_table.verticalHeader().setVisible(False)

        self.rk_lbl = QLabel("총 0명")
        self.rk_lbl.setObjectName("countLabel")

        layout.addWidget(self.rk_table, 1)
        layout.addWidget(self.rk_lbl)

    def _update_ranking(self):
            grade     = self.rk_grade.currentData()
            class_num = self.rk_class.currentData()
            subject   = self.rk_subject.currentText()
            order     = self.rk_order.currentText()

            if grade and class_num:
                students = self.db.get_students_by_class(grade, class_num)
            elif grade:
                students = self.db.get_students_by_grade(grade)
            else:
                students = self.db.get_all_students()

            col_map = {"전체 평균": 7, "국어": 4, "영어": 5, "수학": 6}
            col_idx = col_map[subject]

            reverse  = order == "내림차순"
            students = sorted(students, key=lambda s: s[col_idx], reverse=reverse)

            self.rk_table.blockSignals(True)
            self.rk_table.setRowCount(len(students))
            prev_val  = None
            prev_rank = 0
            for r, s in enumerate(students):
                val = s[col_idx]
                if val != prev_val:
                    rank = r + 1
                    prev_rank = rank
                else:
                    rank = prev_rank
                prev_val = val

                vals = [str(rank), str(s[0]), str(s[1]), str(s[2]), s[3],
                        str(s[4]), str(s[5]), str(s[6]), f"{s[7]:.1f}"]
                for c, v in enumerate(vals):
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(Qt.AlignCenter)
                    if rank == 1:
                        item.setBackground(QColor("#fef9c3"))
                    elif rank == 2:
                        item.setBackground(QColor("#f0fdf4"))
                    elif rank == 3:
                        item.setBackground(QColor("#eff6ff"))
                    self.rk_table.setItem(r, c, item)
            self.rk_table.blockSignals(False)
            self.rk_lbl.setText(f"총 {len(students)}명")

    def refresh(self):
        self._update_ranking()