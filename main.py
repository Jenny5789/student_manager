import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from database.db_manager import DBManager
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 기본 폰트 지정
    font = QFont()
    font.setFamily("Apple SD Gothic Neo")   # macOS
    font.setPointSize(11)
    app.setFont(font)

    db = DBManager()
    db.init_db()

    window = MainWindow(db)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
