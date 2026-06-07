# 📚 학생 성적 관리 시스템

PyQt5 기반 데스크탑 GUI 앱입니다.

## 📁 프로젝트 구조
```
student_manager/
├── main.py                  # 진입점
├── requirements.txt
├── database/
│   └── db_manager.py        # SQLite CRUD
└── views/
    ├── main_window.py       # 메인 창 & 탭
    ├── student_tab.py       # 학생 관리 탭
    ├── score_tab.py         # 성적 입력 탭
    └── stats_tab.py         # 통계 & 시각화 탭
```

## ⚙️ 설치 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 실행
python main.py
```

## 🖥️ 주요 기능

| 탭 | 기능 |
|---|---|
| 👤 학생 관리 | 이름 검색, 학생 추가/삭제, 전체 목록 조회 |
| 📝 성적 관리 | 학년/반 선택 후 성적 직접 입력 & 일괄 저장 |
| 📊 통계 & 시각화 | 과목별 평균 막대그래프, 반별 비교, 히스토그램, 성적 순위 |

## 📝 한글 폰트 설정

- **macOS** : `AppleGothic` (기본값)
- **Windows** : `stats_tab.py` 18번째 줄 → `Malgun Gothic`
- **Linux** : `sudo apt install fonts-nanum` 후 → `NanumGothic`
