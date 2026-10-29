"""기존 학생 DB를 사용하지 않는 로컬 GUI 점검용 실행기."""

import os
from pathlib import Path
import sys
import faulthandler


window = None


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))

    # 현재 PC에서는 이전 venv의 실행기가 다른 PC의 Python을 참조한다.
    # 실행 가능한 Python에서 PyQt5를 찾지 못할 때만 기존 라이브러리를 사용한다.
    try:
        import PyQt5
    except ModuleNotFoundError:
        if sys.version_info[:2] != (3, 12):
            raise SystemExit(
                "기존 venv 라이브러리를 사용하려면 Python 3.12가 필요합니다. "
                "또는 현재 Python 환경에 requirements.txt를 설치하세요."
            )
        sys.path.insert(0, str(root / "venv" / "Lib" / "site-packages"))
        import PyQt5

    # 한글이 포함된 프로젝트 경로에서도 실제 플랫폼 플러그인을 찾도록 지정한다.
    plugins = Path(PyQt5.__file__).resolve().parent / "Qt5" / "plugins" / "platforms"
    if plugins.is_dir():
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugins)
    os.environ["QT_QPA_PLATFORM"] = "windows"

    test_dir = root / ".test-data"
    test_dir.mkdir(exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(test_dir / "matplotlib")

    debug_log = None
    if os.environ.get("STUDENT_MANAGER_DEBUG") == "1":
        debug_log = (test_dir / "debug.log").open("w", encoding="utf-8")
        faulthandler.enable(debug_log, all_threads=True)
        # GUI가 멈춘 동안에도 Python 스레드를 10초마다 기록한다.
        faulthandler.dump_traceback_later(10, repeat=True, file=debug_log)
        print(f"진단 로그: {test_dir / 'debug.log'}", flush=True)

    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import QApplication
    from database.db_manager import DBManager
    from views.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Malgun Gothic", 11))
    db = DBManager(str(test_dir / "student.db"))
    db.init_db()
    print(f"테스트 DB: {db.db_path}", flush=True)
    print("기존 database/student.db는 사용하지 않습니다.", flush=True)
    global window
    window = MainWindow(db)
    window.setWindowTitle("[테스트 모드 v2] 학생 성적 관리 시스템")
    window.show()
    window.raise_()
    window.activateWindow()
    try:
        return app.exec_()
    finally:
        faulthandler.cancel_dump_traceback_later()
        if debug_log:
            debug_log.close()


if __name__ == "__main__":
    sys.exit(main())
