import platform
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox
)

_os = platform.system()
if _os == "Darwin":
    matplotlib.rc("font", family="AppleGothic")
elif _os == "Windows":
    matplotlib.rc("font", family="Malgun Gothic")
else:
    matplotlib.rc("font", family="NanumGothic")
matplotlib.rcParams["axes.unicode_minus"] = False

COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444",
          "#8b5cf6", "#06b6d4", "#f97316", "#84cc16"]


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 4), dpi=96, facecolor="#ffffff")
        self.ax  = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.fig.tight_layout(pad=2.0)


class ClassCompareTab(QWidget):
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

        self.cc_grade = QComboBox()
        self.cc_grade.setFixedWidth(110)
        self.cc_grade.addItem("학년", 0)
        for g in range(1, 4):
            self.cc_grade.addItem(f"{g}학년", g)
        self.cc_grade.currentIndexChanged.connect(self._draw_class_compare)

        self.cc_subject = QComboBox()
        self.cc_subject.setFixedWidth(120)
        self.cc_subject.addItems(["전체 평균", "국어", "영어", "수학"])
        self.cc_subject.currentIndexChanged.connect(self._draw_class_compare)

        row.addWidget(self.cc_grade)
        row.addWidget(self.cc_subject)
        row.addStretch()
        layout.addWidget(grp)

        self.cc_canvas = MplCanvas()
        layout.addWidget(self.cc_canvas, 1)

        self._draw_class_compare()

    # ── 차트 그리기 ──────────────────────────────────────────
    def _draw_class_compare(self):
        grade = self.cc_grade.currentData()
        if not grade or grade == 0:
            self._draw_total_avg()
            return

        rows = self.db.get_class_averages(grade)
        if not rows:
            self.cc_canvas.ax.clear()
            self.cc_canvas.ax.set_title("데이터 없음")
            self.cc_canvas.draw()
            return

        subject = self.cc_subject.currentText()
        classes = [f"{r[0]}반" for r in rows]

        ax = self.cc_canvas.ax
        ax.clear()
        ax.set_facecolor("#fafafa")

        import numpy as np

        if subject == "전체 평균":
            kor  = [r[1] or 0 for r in rows]
            eng  = [r[2] or 0 for r in rows]
            math = [r[3] or 0 for r in rows]

            x = np.arange(len(classes))
            w = 0.25

            ax.bar(x - w, kor,  w, label="국어", color=COLORS[0])
            ax.bar(x,     eng,  w, label="영어", color=COLORS[1])
            ax.bar(x + w, math, w, label="수학", color=COLORS[2])

            ax.set_xticks(x)
            ax.set_xticklabels(classes)

            avg_kor  = sum(kor)  / len(kor)
            avg_eng  = sum(eng)  / len(eng)
            avg_math = sum(math) / len(math)
            ax.axhline(avg_kor,  color=COLORS[0], linestyle="--", linewidth=1, alpha=0.7)
            ax.axhline(avg_eng,  color=COLORS[1], linestyle="--", linewidth=1, alpha=0.7)
            ax.axhline(avg_math, color=COLORS[2], linestyle="--", linewidth=1, alpha=0.7)

            ax.legend(fontsize=10)
            ax.set_title(f"{grade}학년 반별 전체 평균 비교", fontsize=13,
                         fontweight="bold", color="#1e3a5f", pad=10)
        else:
            col_map = {"국어": 1, "영어": 2, "수학": 3}
            col     = col_map[subject]
            values  = [r[col] or 0 for r in rows]

            bars = ax.bar(classes, values, color=COLORS[0], width=0.5,
                          edgecolor="white", linewidth=1.5)

            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.5,
                    f"{val:.1f}",
                    ha="center", va="bottom", fontsize=10,
                    fontweight="bold", color="#1e3a5f"
                )

            avg = sum(values) / len(values)
            ax.axhline(avg, color="#ef4444", linestyle="--",
                       linewidth=1.5, alpha=0.8, label=f"평균 {avg:.1f}점")
            ax.legend(fontsize=10)
            ax.set_title(f"{grade}학년 반별 {subject} 비교", fontsize=13,
                         fontweight="bold", color="#1e3a5f", pad=10)

        ax.set_ylim(0, 110)
        ax.set_ylabel("평균 점수", fontsize=11)
        ax.spines[["top", "right"]].set_visible(False)
        ax.yaxis.grid(True, linestyle="--", alpha=0.5)
        ax.set_axisbelow(True)
        self.cc_canvas.fig.tight_layout(pad=2)
        self.cc_canvas.draw()

    def _draw_total_avg(self):
        import numpy as np

        grades = [1, 2, 3]
        labels = ["1학년", "2학년", "3학년"]
        avgs   = [self.db.get_subject_averages(g) for g in grades]
        kor    = [a[0] for a in avgs]
        eng    = [a[1] for a in avgs]
        math   = [a[2] for a in avgs]

        ax = self.cc_canvas.ax
        ax.clear()
        ax.set_facecolor("#fafafa")

        x = np.arange(len(labels))
        w = 0.25

        ax.bar(x - w, kor,  w, label="국어", color=COLORS[0])
        ax.bar(x,     eng,  w, label="영어", color=COLORS[1])
        ax.bar(x + w, math, w, label="수학", color=COLORS[2])

        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        ax.axhline(sum(kor)/len(kor),   color=COLORS[0], linestyle="--", linewidth=1, alpha=0.7)
        ax.axhline(sum(eng)/len(eng),   color=COLORS[1], linestyle="--", linewidth=1, alpha=0.7)
        ax.axhline(sum(math)/len(math), color=COLORS[2], linestyle="--", linewidth=1, alpha=0.7)

        ax.legend(fontsize=10)
        ax.set_ylim(0, 110)
        ax.set_ylabel("평균 점수", fontsize=11)
        ax.set_title("전체 학년별 과목 평균 비교", fontsize=13,
                     fontweight="bold", color="#1e3a5f", pad=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.yaxis.grid(True, linestyle="--", alpha=0.5)
        ax.set_axisbelow(True)
        self.cc_canvas.fig.tight_layout(pad=2)
        self.cc_canvas.draw()

    def refresh(self):
        self._draw_class_compare()