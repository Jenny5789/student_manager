import sqlite3

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QGroupBox, QComboBox,
    QMessageBox, QLineEdit, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class ScoreItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return self.text() < other.text()


class ScoreTab(QWidget):
    scores_saved = pyqtSignal(object)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self._sort_state = {}
        self._modified = {}
        self._build_ui()
        self._load_students()

    # ── UI 구성 ──────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(self._filter_group())
        layout.addWidget(self._build_table())
        layout.addLayout(self._bottom_bar())

    # ── 필터 ─────────────────────────────────────────────────
    def _filter_group(self):
        grp = QGroupBox("🏫  학생 검색")
        main = QVBoxLayout(grp)
        main.setSpacing(6)

        class_row = QHBoxLayout()
        class_row.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("이름 입력...")
        self.search_input.returnPressed.connect(self._search_by_name)

        btn_search = QPushButton("검색")
        btn_search.clicked.connect(self._search_by_name)

        btn_all = QPushButton("전체 보기")
        btn_all.setObjectName("btnNeutral")
        btn_all.clicked.connect(self._load_all)

        self.combo_grade = QComboBox()

        self.combo_grade.setFixedWidth(90)
        self.combo_grade.addItem("학년", 0)
        for grade in range(1, 4):
            self.combo_grade.addItem(f"{grade}학년", grade)
        self.combo_grade.currentIndexChanged.connect(self._on_grade_changed)

        self.combo_class = QComboBox()
        self.combo_class.setFixedWidth(90)
        self.combo_class.addItem("반", 0)
        for i in range(1, 9):
            self.combo_class.addItem(f"{i}반", i)
        self.combo_class.currentIndexChanged.connect(self._on_class_changed)

        self.combo_num = QComboBox()
        self.combo_num.setFixedWidth(90)
        self.combo_num.addItem("번호", 0)

        class_row.addWidget(self.combo_grade)
        class_row.addWidget(self.combo_class)
        class_row.addWidget(self.combo_num)
        class_row.addWidget(self.search_input, 1)
        class_row.addWidget(btn_search)
        class_row.addWidget(btn_all)

        main.addLayout(class_row)
        return grp

    def _on_grade_changed(self):
        """학년 변경 시 반 드롭다운 초기화"""
        self.combo_class.blockSignals(True)
        self.combo_class.clear()
        self.combo_class.addItem("반", 0)
        for i in range(1, 9):
            self.combo_class.addItem(f"{i}반", i)
        self.combo_class.blockSignals(False)

        self.combo_num.blockSignals(True)
        self.combo_num.clear()
        self.combo_num.addItem("번호", 0)
        self.combo_num.blockSignals(False)

    def _on_class_changed(self):
        """반 변경 시 번호 드롭다운 갱신 (존재하는 번호만)"""
        self.combo_num.blockSignals(True)
        self.combo_num.clear()
        self.combo_num.addItem("번호", 0)
        class_num = self.combo_class.currentData()
        grade = self.combo_grade.currentData()
        if grade and class_num:
            nums = self.db.get_existing_nums(grade, class_num)
            for n in nums:
                self.combo_num.addItem(f"{n}번", n)
        self.combo_num.blockSignals(False)

    # ── 테이블 ────────────────────────────────────────────────
    def _build_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["학년", "반", "번호", "이름", "국어", "영어", "수학", "평균", "비고"]
        )
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setMinimumSectionSize(40)
        self.table.setStyleSheet(
            "QTableWidget QLineEdit {"
            "  min-height: 38px;"
            "  font-size: 13px;"
            "  padding: 0 4px;"
            "}"
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

        hdr = self.table.horizontalHeader()
        for c in [0, 1, 2]:
            hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 300)
        for c in [4, 5, 6, 7]:
            hdr.setSectionResizeMode(c, QHeaderView.Fixed)
            self.table.setColumnWidth(c, 100)
        hdr.setSectionResizeMode(8, QHeaderView.Stretch)

        hdr.sectionClicked.connect(self._on_header_clicked)
        self.table.setSortingEnabled(False)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        self.hint_label = QLabel("※ 국어 · 영어 · 수학 셀을 더블클릭하여 직접 입력하세요.")
        self.hint_label.setStyleSheet("color: gray; font-size: 11px;")

        self.table.itemChanged.connect(self._on_item_changed)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.addWidget(self.hint_label)
        vbox.addWidget(self.table)
        return container

    # ── 하단 바 ──────────────────────────────────────────────
    def _bottom_bar(self):
        row = QHBoxLayout()
        self.lbl_info = QLabel("")
        self.lbl_info.setObjectName("countLabel")

        btn_modified = QPushButton("📋  수정 목록 확인")
        btn_modified.setObjectName("btnNeutral")
        btn_modified.clicked.connect(self._show_modified)

        btn_save = QPushButton("💾  성적 일괄 저장")
        btn_save.setObjectName("btnSuccess")
        btn_save.clicked.connect(self._save_scores)

        row.addWidget(self.lbl_info)
        row.addStretch()
        row.addWidget(btn_modified)
        row.addWidget(btn_save)
        return row

    # ── 데이터 조작 ──────────────────────────────────────────
    def _load_students(self):
        grade     = self.combo_grade.currentData()
        class_num = self.combo_class.currentData()
        num       = self.combo_num.currentData()

        if not grade:
            if class_num:
                QMessageBox.warning(self, "검색 조건", "반으로 검색하려면 학년을 선택하세요.")
                return
            self._load_all()
            return

        if num:
            # 학년 + 반 + 번호
            students = self.db.search_students_by_info(grade, class_num, num)
            self.lbl_info.setText(f"{grade}학년 {class_num}반 {num}번  |  {len(students)}명")
        elif class_num:
            # 학년 + 반
            students = self.db.get_students_by_class(grade, class_num)
            self.lbl_info.setText(f"{grade}학년 {class_num}반  |  {len(students)}명")
        else:
            # 학년 전체
            students = self.db.get_students_by_grade(grade)
            self.lbl_info.setText(f"{grade}학년 전체  |  {len(students)}명")

        self._fill_table(students)

    def _load_all(self):
        self.search_input.clear()
        students = self.db.get_all_students()
        self._fill_table(students)
        self.lbl_info.setText(f"전체  |  {len(students)}명")
    def _search_by_name(self):
        name = self.search_input.text().strip()
        if not name:
            self._load_students()
            return
        students = self.db.search_students(name)
        self._fill_table(students)
        self.lbl_info.setText(f"'{name}' 검색 결과  |  {len(students)}명")
        
    def _fill_table(self, students):
        self.table.blockSignals(True)
        self.table.setRowCount(len(students))
        for r, s in enumerate(students):
            pending = self._modified.get(tuple(s[:3]), {})
            for c in range(4):
                item = QTableWidgetItem(str(s[c]))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, c, item)

            for c in range(4, 7):
                subject = {4: "korean", 5: "english", 6: "math"}[c]
                item = ScoreItem(str(pending.get(subject, s[c])))
                item.setTextAlignment(Qt.AlignCenter)
                if subject in pending:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setForeground(QColor("#1565c0"))
                self.table.setItem(r, c, item)

            try:
                scores = [int(self.table.item(r, c).text()) for c in (4, 5, 6)]
                avg_text = f"{sum(scores) / 3:.1f}" if all(0 <= v <= 100 for v in scores) else "입력 확인"
            except ValueError:
                avg_text = "입력 확인"
            avg_item = ScoreItem(avg_text)
            avg_item.setTextAlignment(Qt.AlignCenter)
            avg_item.setFlags(avg_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(r, 7, avg_item)

            note_item = QTableWidgetItem(str(s[8]) if s[8] else "")
            note_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(r, 8, note_item)

        self.table.blockSignals(False)

    # ── 셀 변경 ──────────────────────────────────────────────
    def _on_item_changed(self, item):
        if item.column() not in (4, 5, 6, 8):
            return

        row = item.row()
        try:
            grade     = int(self.table.item(row, 0).text())
            class_num = int(self.table.item(row, 1).text())
            num       = int(self.table.item(row, 2).text())
        except (ValueError, AttributeError):
            return

        # 비고 칸 → 즉시 DB 저장
        if item.column() == 8:
            self.db.update_note(grade, class_num, num, item.text())
            return

        # 국어/영어/수학 → bold + 파란색
        self.table.blockSignals(True)

        try:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setForeground(QColor("#1565c0"))
            col_name = {4: "korean", 5: "english", 6: "math"}[item.column()]
            key = (grade, class_num, num)
            if key not in self._modified:
                self._modified[key] = {
                    "name": self.table.item(row, 3).text(),
                    "grade": grade, "class_num": class_num, "num": num
                }
            self._modified[key][col_name] = item.text()

            kor  = int(self.table.item(row, 4).text())
            eng  = int(self.table.item(row, 5).text())
            math = int(self.table.item(row, 6).text())
            if not all(0 <= v <= 100 for v in (kor, eng, math)):
                raise ValueError
            avg  = (kor + eng + math) / 3
            self.table.item(row, 7).setText(f"{avg:.1f}")
        except (ValueError, AttributeError):
            self.table.item(row, 7).setText("입력 확인")
        finally:
            self.table.blockSignals(False)

    # ── 헤더 클릭 정렬 ───────────────────────────────────────
    def _on_header_clicked(self, col):
        if col not in (4, 5, 6, 7):
            return

        descending = not self._sort_state.get(col, True)
        self._sort_state = {col: descending}

        col_names = {4: "국어", 5: "영어", 6: "수학", 7: "평균"}
        for c in (4, 5, 6, 7):
            arrow = " ↓" if descending else " ↑"
            text = col_names[c] + (arrow if c == col else "")
            self.table.horizontalHeaderItem(c).setText(text)

        self.table.blockSignals(True)
        order = Qt.DescendingOrder if descending else Qt.AscendingOrder
        self.table.sortItems(col, order)
        self.table.blockSignals(False)

    # ── 수정 목록 팝업 ───────────────────────────────────────
    def _show_modified(self):
        if not self._modified:
            QMessageBox.information(self, "수정 목록", "수정된 항목이 없습니다.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("📋  수정된 항목 목록")
        dlg.setMinimumWidth(520)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel(f"총 {len(self._modified)}명의 성적이 수정되었습니다.")
        lbl.setStyleSheet("font-size: 12px; color: gray;")
        layout.addWidget(lbl)

        tbl = QTableWidget()
        tbl.setColumnCount(7)
        tbl.setHorizontalHeaderLabels(["학년", "반", "번호", "이름", "국어", "영어", "수학"])
        tbl.setRowCount(len(self._modified))
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.verticalHeader().setVisible(False)
        tbl.setAlternatingRowColors(True)
        tbl.horizontalHeader().setStyleSheet(
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
        hdr = tbl.horizontalHeader()
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        for c in [0, 1, 2, 4, 5, 6]:
            hdr.setSectionResizeMode(c, QHeaderView.ResizeToContents)

        for r, (key, data) in enumerate(self._modified.items()):
            vals = [
                str(data["grade"]), str(data["class_num"]), str(data["num"]),
                data["name"],
                data.get("korean", "-"),
                data.get("english", "-"),
                data.get("math", "-")
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                if c in (4, 5, 6) and v and v != "-":
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setForeground(QColor("#1565c0"))
                tbl.setItem(r, c, item)

        layout.addWidget(tbl)

        btn_close = QPushButton("닫기")
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

        dlg.exec_()

    # ── 저장 ────────────────────────────────────────────────
    def has_unsaved_changes(self):
        return bool(self._modified)

    def confirm_unsaved_changes(self, action):
        """탭 이동이나 종료 전에 저장되지 않은 성적을 처리한다."""
        if not self.has_unsaved_changes():
            return True

        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Warning)
        message_box.setWindowTitle("미저장 성적")
        message_box.setText("저장하지 않은 성적 변경이 있습니다.")
        message_box.setInformativeText("저장한 뒤 계속하거나, 변경 내용을 버릴 수 있습니다.")
        save_button = message_box.addButton("저장", QMessageBox.AcceptRole)
        discard_button = message_box.addButton(
            "저장하지 않고 닫기" if action == "종료" else "저장하지 않고 이동",
            QMessageBox.DestructiveRole,
        )
        message_box.addButton("취소", QMessageBox.RejectRole)
        message_box.exec_()

        if message_box.clickedButton() == save_button:
            return self._save_scores()
        return message_box.clickedButton() == discard_button

    def _save_scores(self):
        if not self._modified:
            QMessageBox.information(self, "성적 저장", "저장할 성적 변경이 없습니다.")
            return True

        changes = {}
        errors = []
        for key, data in self._modified.items():
            try:
                fields = {subject: int(data[subject]) for subject in
                          ("korean", "english", "math") if subject in data}
                if any(not 0 <= value <= 100 for value in fields.values()):
                    raise ValueError
                changes[key] = fields
            except ValueError:
                errors.append(f"{key[0]}학년 {key[1]}반 {key[2]}번")

        if errors:
            QMessageBox.warning(
                self, "저장 오류",
                "다음 학생의 점수를 확인하세요: " + ", ".join(errors) + "\n"
                "점수는 0~100 사이의 정수만 입력 가능합니다. 아무 성적도 저장하지 않았습니다."
            )
            return False

        try:
            self.db.update_scores_batch(changes)
        except (sqlite3.Error, ValueError) as exc:
            QMessageBox.warning(self, "저장 실패", f"성적을 저장하지 못했습니다. 수정 내용은 유지됩니다.\n{exc}")
            return False

        count = len(changes)
        self._modified.clear()
        self.table.blockSignals(True)
        try:
            for row in range(self.table.rowCount()):
                key = tuple(int(self.table.item(row, c).text()) for c in range(3))
                if key not in changes:
                    continue
                for column in (4, 5, 6):
                    item = self.table.item(row, column)
                    font = item.font()
                    font.setBold(False)
                    item.setFont(font)
                    item.setForeground(QColor("#000000"))
        finally:
            self.table.blockSignals(False)
        self.scores_saved.emit(list(changes))
        QMessageBox.information(self, "저장 완료", f"✅  검색 결과 밖의 수정 내용을 포함해 {count}명의 성적을 저장했습니다.")
        return True
