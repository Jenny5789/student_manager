from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QPushButton, QLabel,
    QGroupBox, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class StudentTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()
        self.load_all()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        top_row.addWidget(self._search_group(), 5)
        top_row.addWidget(self._add_group(), 5)
        layout.addLayout(top_row)

        layout.addWidget(self._table_section())
        layout.addLayout(self._bottom_bar())

        self._update_search_nums()
        self._update_add_nums()
        self.table.cellChanged.connect(self._on_cell_changed)

    # ── 검색 ─────────────────────────────────────────────────
    def _search_group(self):
        grp = QGroupBox("🔍  학생 검색")
        main = QVBoxLayout(grp)
        main.setSpacing(6)

        # 학년/반/번호 행
        info_row = QHBoxLayout()
        info_row.setSpacing(6)

        self.search_grade = QComboBox()
        self.search_grade.addItem("학년", 0)  # 기본값
        for g in range(1, 4):
            self.search_grade.addItem(f"{g}학년", g)
        self.search_grade.currentIndexChanged.connect(self._update_search_nums)

        self.search_class = QComboBox()
        self.search_class.addItem("반", 0)  # 기본값
        for c in range(1, 9):
            self.search_class.addItem(f"{c}반", c)
        self.search_class.currentIndexChanged.connect(self._update_search_nums)

        self.search_num = QComboBox()
        self.search_num.addItem("번호", 0)  # 기본값

        info_row.addWidget(self.search_grade, 1)
        info_row.addWidget(self.search_class, 1)
        info_row.addWidget(self.search_num, 1)

        # 이름/전체보기/검색 행
        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("이름 입력...")
        self.search_input.returnPressed.connect(self._do_search)

        btn_all = QPushButton("전체 보기")
        btn_all.setObjectName("btnNeutral")
        btn_all.clicked.connect(self.load_all)

        btn_search = QPushButton("검색")
        btn_search.clicked.connect(self._do_search)

        name_row.addWidget(self.search_input, 1)
        name_row.addWidget(btn_all)
        name_row.addWidget(btn_search)

        main.addLayout(info_row)
        main.addLayout(name_row)
        return grp

    def _update_search_nums(self):
        grade = self.search_grade.currentData()
        class_num = self.search_class.currentData()
        self.search_num.blockSignals(True)
        self.search_num.clear()
        self.search_num.addItem("번호", 0)
        if grade and class_num:
            nums = self.db.get_existing_nums(grade, class_num)
            for n in nums:
                self.search_num.addItem(f"{n}번", n)
        self.search_num.blockSignals(False)

    # ── 추가 ─────────────────────────────────────────────────
    def _add_group(self):
        grp = QGroupBox("➕  학생 추가")
        main_layout = QVBoxLayout(grp)
        main_layout.setSpacing(6)

        # 학년/반/번호 행
        info_row = QHBoxLayout()
        info_row.setSpacing(6)

        self.inp_grade = QComboBox()
        self.inp_grade.addItem("학년", 0)
        for g in range(1, 4):
            self.inp_grade.addItem(f"{g}학년", g)
        self.inp_grade.currentIndexChanged.connect(self._update_add_nums)

        self.inp_class = QComboBox()
        self.inp_class.addItem("반", 0)
        for c in range(1, 9):
            self.inp_class.addItem(f"{c}반", c)
        self.inp_class.currentIndexChanged.connect(self._update_add_nums)

        self.inp_num = QComboBox()
        self.lbl_last_num = QLabel()
        self.lbl_last_num.setStyleSheet("color: gray; font-size: 11px;")

        info_row.addWidget(self.inp_grade, 1)
        info_row.addWidget(self.inp_class, 1)
        info_row.addWidget(self.inp_num, 1)

        # 이름/추가 행
        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("이름")

        btn_add = QPushButton("추가")
        btn_add.setObjectName("btnSuccess")
        btn_add.clicked.connect(self._add_student)

        name_row.addWidget(self.inp_name, 1)
        name_row.addWidget(btn_add)

        main_layout.addLayout(info_row)
        main_layout.addLayout(name_row)
        main_layout.addWidget(self.lbl_last_num)

        return grp

    def _update_add_nums(self):
        grade = self.inp_grade.currentData()
        class_num = self.inp_class.currentData()

        self.inp_num.blockSignals(True)
        self.inp_num.clear()
        self.inp_num.addItem("번호", 0)
        self.inp_num.blockSignals(False)
        self.lbl_last_num.setText("")

        if not grade or not class_num:
            return

        last = self.db.get_last_num(grade, class_num)
        nums = self.db.get_available_nums(grade, class_num)
        self.inp_num.blockSignals(True)
        self.inp_num.clear()
        for n in nums:
            self.inp_num.addItem(f"{n}번", n)
        self.inp_num.blockSignals(False)
        if last == 0:
            self.lbl_last_num.setText(
                f"※ {grade}학년 {class_num}반은 1번부터 추가 가능합니다."
            )
        else:
            self.lbl_last_num.setText(
                f"※ {grade}학년 {class_num}반은 {last + 1}번부터 추가 가능합니다."
            )

    # ── 테이블 ────────────────────────────────────────────────
    def _table_section(self):
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["학년", "반", "번호", "이름", "국어", "영어", "수학", "평균", "비고"]
        )

        # 헤더 색상 진하게
        header_style = (
            "QHeaderView::section {"
            "  background-color: #b0bec5;"
            "  color: #1a1a2e;"
            "  font-weight: 500;"
            "  padding: 4px;"
            "  border: none;"
            "  border-right: 0.5px solid #90a4ae;"
            "  border-bottom: 1px solid #78909c;"
            "}"
        )
        self.table.horizontalHeader().setStyleSheet(header_style)

        hdr = self.table.horizontalHeader()
        for c in [0, 1, 2]:
            hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 300)   # 이름 너비 
        for c in [4, 5, 6, 7]:
            hdr.setSectionResizeMode(c, QHeaderView.Fixed)
            self.table.setColumnWidth(c, 100)  # 국영수평균 너비
        hdr.setSectionResizeMode(8, QHeaderView.Stretch)  # 비고가 나머지 차지

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        return self.table

    # ── 하단 바 ──────────────────────────────────────────────
    def _bottom_bar(self):
        row = QHBoxLayout()
        self.lbl_count = QLabel("총 0명")
        self.lbl_count.setObjectName("countLabel")

        btn_del = QPushButton("🗑  선택 학생 삭제")
        btn_del.setObjectName("btnDanger")
        btn_del.clicked.connect(self._delete_student)

        row.addWidget(self.lbl_count)
        row.addStretch()
        row.addWidget(btn_del)
        return row

    # ── 데이터 ───────────────────────────────────────────────
    def load_all(self):
        self.search_input.clear()
        self._fill_table(self.db.get_all_students())

    def _do_search(self):
        name = self.search_input.text().strip()
        if name:
            self._fill_table(self.db.search_students(name))
            return

        grade     = self.search_grade.currentData()
        class_num = self.search_class.currentData()
        num       = self.search_num.currentData()

        if not grade:
            # 전체 조회
            self._fill_table(self.db.get_all_students())
        elif not class_num:
            # 학년 전체
            self._fill_table(self.db.get_students_by_grade(grade))
        elif not num:
            # 학년+반 전체
            self._fill_table(self.db.get_students_by_class(grade, class_num))
        else:
            # 학년+반+번호
            self._fill_table(self.db.search_students_by_info(grade, class_num, num))

    def _do_search_info(self):
        grade     = self.search_grade.currentData()
        class_num = self.search_class.currentData()
        num       = self.search_num.currentData()
        self._fill_table(self.db.search_students_by_info(grade, class_num, num))

    def _fill_table(self, students):
        self.table.blockSignals(True)
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(len(students))
        for r, s in enumerate(students):
            for c, val in enumerate(s[:8]):
                text = f"{val:.1f}" if c == 7 else str(val)
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, c, item)
            note_item = QTableWidgetItem(str(s[8]) if s[8] else "")
            note_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(r, 8, note_item)
        self.lbl_count.setText(f"총 {len(students)}명")
        self.table.setUpdatesEnabled(True)
        self.table.blockSignals(False)

    def _on_cell_changed(self, row, col):
        if col != 8:
            return
        try:
            grade     = int(self.table.item(row, 0).text())
            class_num = int(self.table.item(row, 1).text())
            num       = int(self.table.item(row, 2).text())
            note      = self.table.item(row, 8).text()
            self.table.blockSignals(True)
            self.db.update_note(grade, class_num, num, note)
            self.table.blockSignals(False)
        except (ValueError, AttributeError):
            self.table.blockSignals(False)

    def _add_student(self):
        name = self.inp_name.text().strip()
        if not name:
            QMessageBox.warning(self, "입력 오류", "이름을 입력하세요.")
            return
        grade     = self.inp_grade.currentData()
        class_num = self.inp_class.currentData()
        num       = self.inp_num.currentData()
        if num is None:
            QMessageBox.warning(self, "입력 오류", "추가 가능한 번호가 없습니다.")
            return
        ok, msg = self.db.add_student(grade, class_num, num, name)
        if ok:
            self.inp_name.clear()
            self._update_add_nums()
            self._update_search_nums()
            self.load_all()
            self._ask_score_input(grade, class_num, num, name)
        else:
            QMessageBox.warning(self, "추가 실패", msg)

    def _delete_student(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "선택 오류", "삭제할 학생을 먼저 선택하세요.")
            return
        grade     = int(self.table.item(row, 0).text())
        class_num = int(self.table.item(row, 1).text())
        num       = int(self.table.item(row, 2).text())
        name      =     self.table.item(row, 3).text()
        reply = QMessageBox.question(
            self, "삭제 확인",
            f"정말로 [{name}] ({grade}학년 {class_num}반 {num}번) 학생을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_student(grade, class_num, num)
            self._update_add_nums()
            self._update_search_nums()
            self.load_all()

    def _ask_score_input(self, grade, class_num, num, name):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QSpinBox

        reply = QMessageBox.question(
            self, "성적 입력",
            f"✅  {name} 학생이 추가되었습니다.\n지금 바로 성적을 입력하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"📝  {name} 성적 입력")
        dlg.setMinimumWidth(320)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel(f"{grade}학년 {class_num}반 {num}번  |  {name}")
        lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl)

        # 국어
        kor_row = QHBoxLayout()
        kor_row.addWidget(QLabel("국어"))
        kor_spin = QSpinBox()
        kor_spin.setRange(0, 100)
        kor_spin.setValue(0)
        kor_row.addWidget(kor_spin)
        layout.addLayout(kor_row)

        # 영어
        eng_row = QHBoxLayout()
        eng_row.addWidget(QLabel("영어"))
        eng_spin = QSpinBox()
        eng_spin.setRange(0, 100)
        eng_spin.setValue(0)
        eng_row.addWidget(eng_spin)
        layout.addLayout(eng_row)

        # 수학
        math_row = QHBoxLayout()
        math_row.addWidget(QLabel("수학"))
        math_spin = QSpinBox()
        math_spin.setRange(0, 100)
        math_spin.setValue(0)
        math_row.addWidget(math_spin)
        layout.addLayout(math_row)

        # 버튼
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("나중에")
        btn_cancel.setObjectName("btnNeutral")
        btn_cancel.clicked.connect(dlg.reject)

        btn_save = QPushButton("저장")
        btn_save.setObjectName("btnSuccess")
        def do_save():
            self._save_new_score(
                dlg, grade, class_num, num,
                kor_spin.value(), eng_spin.value(), math_spin.value()
            )
        btn_save.clicked.connect(do_save)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

        dlg.exec_()

    def _save_new_score(self, dlg, grade, class_num, num, kor, eng, math):
        self.db.update_scores(grade, class_num, num, kor, eng, math)
        dlg.accept()
        self.load_all()
        QMessageBox.information(self, "저장 완료", "✅  성적이 저장되었습니다.")