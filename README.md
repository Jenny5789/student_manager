# Student Manager &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<small><small><small>2026.06</small></small></small>

Python, PyQt5, SQLite로 만든 학생 정보·성적 관리 데스크톱 앱.

학생·성적 CRUD, 조건별 검색, 성적 순위, 학급별 평균 그래프를 제공하고, 성적 일괄 저장은 트랜잭션으로 묶어 오류가 나면 전체를 되돌림.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=python&logoColor=white)
![unittest](https://img.shields.io/badge/unittest-3776AB?style=for-the-badge&logo=python&logoColor=white)

<img src="images/tab2.png" width="600" alt="성적 관리 화면">

## 핵심 코드

### 수정 내용 모아 두기

[views/score_tab.py](views/score_tab.py)

고친 점수를 `(학년, 반, 번호)` 키의 딕셔너리에 모아 두어, 검색 조건을 바꿔도 수정 내용이 유지되고 저장할 때 한 번에 반영.

```python
key = (grade, class_num, num)
if key not in self._modified:
    self._modified[key] = {
        "name": self.table.item(row, 3).text(),
        "grade": grade, "class_num": class_num, "num": num
    }
self._modified[key][col_name] = item.text()   # 수정한 과목만 기록
```

### 성적 일괄 저장과 롤백

[database/db_manager.py](database/db_manager.py)

여러 학생의 성적을 하나의 트랜잭션으로 저장해, 한 명이라도 오류가 나면 전체를 되돌림.

```python
def update_scores_batch(self, changes):
    """수정된 과목만 반영하며, 실패하면 전체 성적 변경을 롤백한다."""
    conn = self.get_connection()
    try:
        with conn:                                   # 오류 시 자동 롤백
            conn.execute("BEGIN IMMEDIATE")
            for key, fields in changes.items():
                row = conn.execute(
                    "SELECT korean,english,math FROM students "
                    "WHERE grade=? AND class_num=? AND num=?", key
                ).fetchone()
                if row is None:
                    raise ValueError(f"학생이 존재하지 않습니다: {key}")
                # 수정하지 않은 과목은 DB 점수를 그대로 사용
                scores = [fields.get(subject, row[i]) for i, subject in
                          enumerate(("korean", "english", "math"))]
                if any(type(value) is not int or not 0 <= value <= 100
                       for value in scores):
                    raise ValueError("점수는 0~100 사이의 정수여야 합니다.")
                conn.execute(
                    "UPDATE students SET korean=?,english=?,math=?,average=? "
                    "WHERE grade=? AND class_num=? AND num=?",
                    (*scores, sum(scores) / 3, *key)
                )
    finally:
        conn.close()
```

## 문제 해결

<img src="images/problem-solving-process.png" width="100%" alt="문제 해결과 개선 과정">

| 문제 | 개선 |
|---|---|
| 학년·반을 고르지 않아도 학생 추가됨 | 저장 전 학년·반·번호와 이름 검사 |
| 저장 중 오류가 나면 일부 성적만 저장됨 | 단일 트랜잭션과 전체 롤백 ([핵심 코드](#성적-일괄-저장과-롤백)) |
| 저장·탭 이동 시 화면 멈춤 (`debug.log`로 675명 × 9열 표 재생성 확인) | 전체 표 재생성을 없애고 바뀐 학생 행만 갱신 |

## 주요 기능

| 기능 | 설명 |
|---|---|
| 학생 관리 | 학년·반·번호 또는 이름 검색, 학생 추가·삭제, 비고 수정<br>필수 입력 누락·공백 이름 검사 |
| 성적 관리 | 국어·영어·수학 점수 편집과 일괄 저장, 0~100 정수 검증, 평균 계산<br>점수·평균 기준 정렬, 미저장 상태에서 탭 이동·종료 시 저장 여부 확인 |
| 학급별 비교 | 선택 학년의 학급별 과목 평균 그래프(Matplotlib) |
| 조건별 조회 | 학년·반·과목·점수 조건으로 학생 조회 |
| 성적 순위 | 과목별 성적 순위와 정렬 조건 선택 |
| 코드 구조 | 화면(`views/`)은 입력과 표시만, `DBManager`는 DB 처리만 담당<br>저장·검색·정렬·롤백·탭 이동은 별도 테스트 DB로 unittest 검증(`tests/`) |

<details>
<summary>전체 화면 보기</summary>

| 학생 관리 | 성적 입력 창 |
|---|---|
| <img src="images/tab0.png" width="400" alt="학생 관리"> | <img src="images/tab1.png" width="400" alt="성적 입력 창"> |

| 학급별 비교 그래프 | 조건별 조회 |
|---|---|
| <img src="images/tab3.png" width="400" alt="학급별 비교 그래프"> | <img src="images/tab4.png" width="400" alt="조건별 조회"> |

| 성적 순위 | |
|---|---|
| <img src="images/tab5.png" width="400" alt="성적 순위"> | |

</details>

## 파일 구조

```
student_manager/
├── main.py                  # 앱 시작점
├── requirements.txt         # 실행 의존성
├── database/
│   └── db_manager.py        # DB 초기화·CRUD·통계 조회
├── views/
│   ├── main_window.py       # 탭 구성·화면 연결
│   ├── student_tab.py       # 학생 관리
│   ├── score_tab.py         # 성적 편집·저장
│   ├── stats_class_tab.py   # 학급별 평균 그래프
│   ├── stats_search_tab.py  # 조건별 조회
│   └── stats_ranking_tab.py # 성적 순위
├── tests/                   # 저장·검색·상태 관리 검증
└── images/                  # README 스크린샷
```

## 실행 방법

Python 3.x.

```powershell
git clone https://github.com/Jenny5789/student_manager.git
cd student_manager

python -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python main.py
```

- DB 위치: `database/student.db`
- 학생 테이블이 비어 있으면 샘플 데이터 자동 생성
