import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog  # CSV 파일 저장 위치를 사용자가 직접 선택하게 하는 filedialog 모듈 호출
import datetime
import calendar
import matplotlib.pyplot as plt
import csv  # 엑셀(CSV) 저장을 위해 추가된 기본 라이브러리
import os  # 저장된 CSV 파일을 열고 임시 저장 파일을 교체하기 위해 사용하는 기본 라이브러리

file_name = "schedules.txt"
schedules = []  # [할일, 시작일, 종료일, 우선순위, 메모] 형태로 저장
current_rows = []  # 현재 결과창에 실제로 표시된 일정들을 저장

CHART_MAX_DAYS = 366  # 시각화 시 한 일정이 너무 긴 기간을 차지하면 멈추기 위한 최대 일수


def is_valid_date(text):
    parts = text.split("-")  # 입력된 문자열 text를 하이픈 기호 기준으로 나눔
    if len(parts) != 3:  # 만약 나누어진 파트 리스트의 요소 개수가 3이 != 아니라면
        return False  # 형식 이탈로 거짓으로 반환

    y = parts[0]  # 첫 번째 파트를 연도 y에 지정
    m = parts[1]  # 두 번째 파트를 월 m에 지정
    d = parts[2]  # 세 번째 파트를 일 d에 지정

    if len(y) != 4 or len(m) != 2 or len(d) != 2:  # 만약 연도y가 네 자리가 아니거나 월m이 두 자리가 아니거나 일d가 두 자리가 아니라면
        return False  # 자릿수 불일치 에러로 거짓으로 반환

    if not (y.isdigit() and m.isdigit() and d.isdigit()):  # 만약 연도y, 월m, 일d가 모두 숫자가 아니라면
        return False  # 문자 포함 오류로 거짓으로 반환

    y = int(y)  # 문자열 연도 y를 정수로 변환
    m = int(m)  # 문자열 월 m을 정수로 변환
    d = int(d)  # 문자열 일 d를 정수로 변환

    if y < 1 or y > 9999:  # 만약 연도 y가 1보다 < 작거나 9999보다 > 크다면
        return False  # 범위 초과 오류로 거짓으로 반환
    if m < 1 or m > 12:  # 만약 월 m이 1보다 < 작거나 12보다 > 크다면
        return False  # 범위 초과 오류로 거짓으로 반환

    last_days_of_m = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # 평년 기준 각 월의 마지막 날짜를 리스트 상자에 설정

    if y % 400 == 0 or (y % 4 == 0 and y % 100 != 0):  # 만약 연도 y가 윤년 계산 공식 조건을 충족하는 해라면
        last_days_of_m[1] = 29  # 2월의 마지막 날짜 요소를 29일로 변경 설정

    if d < 1 or d > last_days_of_m[m - 1]:  # 만약 일 d 수치가 1보다 < 작거나 해당 월의 마지막 날짜 요소보다 > 크다면
        return False  # 존재하지 않는 날짜 오류로 거짓으로 반환

    return True  # 모든 까다로운 조건을 무사히 통과했다면 진짜 날짜이므로 참으로 반환


def parse_date_str(text):
    parts = text.split("-")  # 문자열 text를 하이픈(-) 기준으로 나눔
    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))  # 나누어진 파트들을 정수로 변환하여 날짜객체로 반환


def date_to_str(d):
    return d.isoformat()  # 날짜객체 d를 YYYY-MM-DD 형식의 문자열로 변환해서 반환


def has_forbidden_char(text):
    return "|" in text or "\n" in text or "\r" in text  # 만약 text 문자열 안에 금지된 기호 문자들이 포함되어 있으면 참으로 반환


def date_error_message():
    return "날짜는 실제 존재하는 날짜를 YYYY-MM-DD 형식으로 입력하세요. 예: 2026-05-24"  # 날짜 형식 오류 안내 문구를 반환


def forbidden_char_message():
    return "입력란에는 | 문자와 줄바꿈 문자를 사용할 수 없습니다."  # 금지 문자 사용 오류 안내 문구를 반환


def valid_priority(priority):
    return priority in ["긴급", "높음", "보통", "낮음"]  # 만약 priority 문자열이 허용 리스트 안에 매칭되어 존재하면 참으로 반환


def is_valid_schedule_row(s):
    if len(s) != 5:  # 만약 일정 리스트 s의 요소 개수가 5개가 != 아니라면
        return False  # 거짓으로 반환
    if s[0] == "":  # 만약 첫 번째 할일 요소 s[0]이 == "" 빈칸이면
        return False  # 거짓으로 반환
    if has_forbidden_char(s[0]) or has_forbidden_char(s[4]):  # 만약 할일이나 메모 요소에 금지 문자가 포함되어 있다면
        return False  # 거짓으로 반환
    if not is_valid_date(s[1]):  # 만약 시작일 요소 s[1]이 올바른 날짜 형식이 아니라면
        return False  # 거짓으로 반환
    if not is_valid_date(s[2]):  # 만약 종료일 요소 s[2]가 올바른 날짜 형식이 아니라면
        return False  # 거짓으로 반환
    if s[1] > s[2]:  # 만약 시작일 s[1]이 종료일 s[2]보다 > 크다면
        return False  # 논리적 모순이므로 거짓으로 반환
    if not valid_priority(s[3]):  # 만약 우선순위 요소 s[3]이 올바른 규격이 아니라면
        return False  # 거짓으로 반환
    return True  # 모든 조건을 통과하면 참으로 반환



def open_range_calendar(parent, set_range_func):
    win = tk.Toplevel(parent)  # 부모 창 위에 새로 생성된 독립된 보조 창을 win 변수에 저장
    win.title("시작일을 선택하세요 (1/2)")  # 보조 창 win의 제목을 "시작일을 선택하세요 (1/2)" 문구로 설정
    win.resizable(False, False)  # 보조 창 win의 가로 세로 크기 변경을 불가능하게 설정
    win.grab_set()  # 이 보조 창이 켜져 있는 동안 다른 창을 누르지 못하도록 독점 설정

    view = datetime.date.today()  # 현재 시점 오늘 날짜를 변수 view에 저장
    state = {"year": view.year, "month": view.month}  # 현재 달력의 연도와 월을 기억할 딕셔너리를 변수 state에 설정
    clicks = []  # 사용자가 클릭한 날짜들을 담을 빈 리스트 clicks 설정

    body = tk.Frame(win)  # 보조 창 win 안에 달력 요소를 배치할 프레임을 생성하여 변수 body에 저장
    body.pack(padx=12, pady=10)  # 달력 프레임 body를 가로 여백 12, 세로 여백 10으로 배치

    nav = tk.Frame(body)  # 연도와 월 이동 버튼을 담을 상단 프레임을 생성하여 변수 nav에 저장
    nav.pack(pady=(0, 6))  # 이동 프레임 nav를 상단 여백 0, 하단 여백 6으로 배치

    title_label = tk.Label(nav, text="", font=("Arial", 12, "bold"))  # 연도와 월 글자를 표시할 라벨을 생성하여 변수 title_label에 저장
    title_label.pack(side=tk.LEFT, padx=10)  # 연도월 라벨을 왼쪽에 배치하고 가로 여백 10 설정

    grid_frame = tk.Frame(body)  # 날짜 숫자 버튼들을 격자로 배치할 프레임을 생성하여 변수 grid_frame에 저장
    grid_frame.pack()  # 격자 프레임 grid_frame을 배치

    def change_month(delta):  # 달을 변경하는 내부 함수 정의
        y = state["year"]  # 현재 state 딕셔너리의 연도 값을 변수 y에 저장
        m = state["month"] + delta  # 현재 월 값에 변화량 delta를 더한 값을 변수 m에 저장

        if m < 1:  # 만약 변경된 월 m이 1보다 < 작다면
            m = 12  # 월 m을 12로 재조정 설정
            y = y - 1  # 연도 y 수치를 1 감소 차감 계산
        elif m > 12:  # 만약 변경된 월 m이 12보다 > 크다면
            m = 1  # 월 m을 1로 재조정 설정
            y = y + 1  # 연도 y 수치를 1 증가 가산 계산

        if y < 1 or y > 9999:  # 만약 연도 y가 1보다 < 작거나 9999보다 > 크다면
            messagebox.showerror("이동 오류", "달력은 0001년부터 9999년까지만 이동할 수 있습니다.", parent=win)  # 이동 오류 메시지 창을 보조 창 win 위에 띄움
            return  # 함수 실행 즉시 종료

        state["year"] = y  # 변경된 연도 y를 state 딕셔너리에 업데이트 최신화
        state["month"] = m  # 변경된 월 m을 state 딕셔너리에 업데이트 최신화
        render_days()  # 달력 날짜 화면을 새로고침 리드로잉

    tk.Button(nav, text="<", width=3, command=lambda: change_month(-1)).pack(side=tk.LEFT)  # 이전 달 화살표 단추를 왼쪽 정렬로 팩 배치
    tk.Button(nav, text=">", width=3, command=lambda: change_month(1)).pack(side=tk.RIGHT)  # 다음 달 화살표 단추를 오른쪽 정렬로 팩 배치

    def pick_date(day):  # 사용자가 날짜 숫자를 클릭했을 때 실행되는 내부 함수 정의
        picked = datetime.date(state["year"], state["month"], day)  # 선택된 연, 월, 일로 날짜객체를 생성하여 변수 picked에 저장

        if len(clicks) == 0:  # 만약 클릭 리스트 clicks의 요소 개수가 == 0 이면
            clicks.append(picked)  # clicks 리스트에 선택한 날짜 picked 추가
            win.title("종료일을 선택하세요 (2/2)")  # 보조 창 win의 제목을 종료일 선택 안내로 변경 설정
            render_days()  # 선택 상태를 반영하기 위해 달력 날짜 화면을 새로고침

        elif len(clicks) == 1:  # 만약 클릭 리스트 clicks의 요소 개수가 == 1 이면
            start_date_obj = clicks[0]  # 클릭 리스트의 첫 번째 요소를 시작일 날짜객체 변수 start_date_obj에 지정

            if picked < start_date_obj:  # 만약 선택한 날짜 picked가 시작일보다 < 작다면
                messagebox.showerror("선택 오류", "종료일은 시작일보다 빠를 수 없습니다.", parent=win)  # 선택 오류 메시지 창을 보조 창 win 위에 띄움
                return  # 함수 실행 즉시 종료

            start_date = date_to_str(start_date_obj)  # 시작일 날짜객체를 YYYY-MM-DD 문자열로 변환하여 변수 start_date에 저장
            end_date = date_to_str(picked)  # 종료일 날짜객체를 YYYY-MM-DD 문자열로 변환하여 변수 end_date에 저장
            set_range_func(start_date, end_date)  # 전달받은 콜백 함수 set_range_func에 시작일과 종료일 문자열을 넘겨 실행
            win.destroy()  # 작업이 완료된 보조 창 win을 닫음 파괴

    def render_days():  # 달력의 일자 버튼들을 화면에 그려주는 내부 함수 정의
        for child in grid_frame.winfo_children():  # grid_frame 격자 프레임 내부의 모든 하위 요소를 하나씩 child 변수에 넣고 반복
            child.destroy()  # 기존에 그려진 하위 요소 child를 화면에서 제거 철거

        y = state["year"]  # 현재 state 딕셔너리의 연도 값을 변수 y에 저장
        m = state["month"]  # 현재 state 딕셔너리의 월 값을 변수 m에 저장
        today = datetime.date.today()  # 현재 시점 오늘 날짜를 변수 today에 저장

        title_label.config(text=f"{y}년 {m}월")  # 상단 연도월 라벨의 텍스트를 현재 연도와 월 문구로 최신화 수정 설정

        weekdays = ["월", "화", "수", "목", "금", "토", "일"]  # 요일 이름을 순서대로 리스트 weekdays에 저장

        for col, name in enumerate(weekdays):  # 요일 리스트에서 인덱스 col과 이름 name을 하나씩 꺼내어 반복
            tk.Label(grid_frame, text=name, width=4).grid(row=0, column=col, pady=2)  # 요일 이름 라벨을 격자의 0행 col열에 배치

        month_days = calendar.monthcalendar(y, m)  # 한 달 달력 구조를 2차원 리스트 행렬 형태로 변수 month_days에 저장

        for row_index, week in enumerate(month_days, start=1):  # 달력 주 목록에서 행 번호 row_index와 주 리스트 week를 하나씩 꺼내어 1번 행부터 반복
            for col_index, day in enumerate(week):  # 한 주의 일 목록에서 열 번호 col_index와 일 숫자 day를 하나씩 꺼내어 반복
                if day == 0:  # 만약 해당 칸의 일 숫자 day가 == 0 이면
                    tk.Label(grid_frame, text="", width=4).grid(row=row_index, column=col_index)  # 빈 라벨을 생성하여 격자의 row_index행 col_index열에 배치
                    continue  # 아래 코드를 실행하지 않고 다음 칸 반복으로 건너뜀

                day_date = datetime.date(y, m, day)  # 현재 칸의 연, 월, 일 숫자로 날짜객체를 생성해 변수 day_date에 저장

                btn_text = str(day)  # 날짜 숫자를 문자열로 변환하여 버튼 텍스트 변수 btn_text에 저장
                if day_date == today:  # 만약 현재 날짜 day_date가 오늘 날짜와 == 같으면
                    btn_text = str(day) + "*"  # 버튼 텍스트 뒤에 오늘 표시 기호 *를 연결하여 저장

                state_btn = tk.NORMAL  # 버튼의 기본 상태를 클릭 가능 상태인 tk.NORMAL로 설정
                if day_date < today:  # 만약 현재 날짜 day_date가 오늘보다 < 작다면(과거라면)
                    state_btn = tk.DISABLED  # 버튼 상태를 비활성화 잠금 상태인 tk.DISABLED로 설정 지정

                btn = tk.Button(
                    grid_frame,
                    text=btn_text,
                    width=4,
                    state=state_btn,
                    command=lambda d=day: pick_date(d)
                )  # 날짜 숫자 버튼 위젯을 생성하고 클릭 시 pick_date 내부 함수가 가동되도록 연결

                if len(clicks) == 1 and day_date == clicks[0]:  # 만약 클릭된 날짜가 == 1개이고 현재 날짜가 첫 번째 클릭 날짜와 == 같으면
                    btn.config(bg="lightblue", relief=tk.SUNKEN, bd=3)  # 선택 상태 시각 효과를 위해 버튼의 배경색과 눌림 모양을 변경 설정

                btn.grid(row=row_index, column=col_index, padx=1, pady=1)  # 날짜 버튼을 격자의 row_index행 col_index열에 배치

    render_days()  # 보조 창이 열릴 때 처음 한 번 달력 날짜들을 화면에 그림
    tk.Label(body, text="* 오늘 날짜", font=("Arial", 9)).pack(pady=(6, 2))  # 오늘 날짜 표시 기호 안내 라벨을 하단에 배치
    tk.Label(body, text="파란색/눌림 표시: 선택한 시작일", font=("Arial", 9)).pack(pady=(0, 2))  # 파란색 선택 표시 안내 라벨을 하단에 배치
    tk.Label(body, text="단일 일정은 같은 날짜를 두 번 누르세요.", font=("Arial", 9)).pack(pady=(0, 4))  # 단일 일정 선택 가이드 라벨을 하단에 배치



def make_dday_text(target_date):
    target = parse_date_str(target_date)  # 목표일 문자열을 날짜객체로 파싱 전환하여 변수 target에 저장
    diff = (target - datetime.date.today()).days  # 목표일 객체에서 오늘 날짜 객체를 뺀 경과 일수 수치를 변수 diff에 저장

    if diff > 0:  # 만약 연산 일수 diff 숫자가 0보다 > 크다면
        return f"D-{diff}"  # D-남은일 형식 문자열을 반환
    elif diff == 0:  # 만약 연산 일수 diff 숫자가 정확하게 == 0 상태에 해당하면
        return "D-Day"  # D-Day 고정 문자열을 반환
    else:  # 만약 연산 일수 diff 숫자가 0보다 작은 과거 상황이라면
        return f"D+{abs(diff)}"  # D+지나간일 형식 문자열을 반환


def load_schedules():
    schedules.clear()  # 기존 전체 일정 리스트 schedules 내용을 깨끗하게 비움 리셋
    skipped_count = 0  # 저장 파일에서 형식이 맞지 않아 건너뛴 줄 개수를 세기 위한 변수

    try:  # 파일 생성이나 읽기 과정에서 오류가 날 가능성을 대비
        open(file_name, "a", encoding="utf-8").close()  # 파일이 없으면 새로 만들어 개설하고 바로 닫음 셋팅

        with open(file_name, "r", encoding="utf-8") as f:  # 표준 utf-8 인코딩 형식으로 저장소 파일을 파일읽기모드로 엶
            for line in f:  # 파일 객체 f로부터 줄글 문장을 한 줄씩 꺼내 내부 변수 line에 주입하며 반복
                data = line.strip().split("|")  # 줄글 문장의 양쪽 공백을 제거하고 파이프 기호 기준으로 쪼개어 가공 리스트 data로 전환
                row = None  # 일정 행 데이터를 담을 임시 변수 row를 None 상태로 초기화 설정

                if len(data) == 5:  # 만약 데이터 리스트 data의 요소 개수가 == 5 상태에 해당하면
                    row = [data[0], data[1], data[2], data[3], data[4]]  # 온전한 5대 필드 구성 데이터를 변수 row에 리스트로 저장
                elif len(data) == 4:  # 만약 데이터 리스트 data의 요소 개수가 == 4 상태에 해당하면 (구버전 데이터 호환)
                    row = [data[0], data[1], data[1], data[2], data[3]]  # 시작일과 종료일을 동일하게 설정하여 5대 필드 리스트로 변수 row에 저장
                elif len(data) > 5:  # 만약 데이터 리스트 data의 요소 개수가 5보다 > 크다면
                    end_d = data[5] if len(data) > 5 and is_valid_date(data[5]) else data[1]  # 6번째 요소가 정상 날짜면 종료일로 삼고 아니면 시작일을 종료일로 지정해 변수 end_d에 저장
                    row = [data[0], data[1], end_d, data[2], data[3]]  # 가공 완료된 5대 필드 데이터를 변수 row에 리스트로 저장

                if row is not None and is_valid_schedule_row(row):  # 만약 변수 row가 None이 아니고 올바른 일정 형식 조건에 합격한다면
                    schedules.append(row)  # 전역 보관소 주머니 schedules 리스트 맨 뒤에 해당 행 데이터를 추가 담기
                elif line.strip() != "":  # 만약 빈 줄이 아닌데도 올바른 일정 형식이 아니라면
                    skipped_count = skipped_count + 1  # 무시된 줄 개수를 1 증가시켜 사용자에게 알릴 준비

        if skipped_count > 0:  # 만약 저장 파일에서 무시된 줄이 하나 이상 존재한다면
            messagebox.showwarning("파일 읽기 경고", "저장 파일에서 형식이 맞지 않는 일정 " + str(skipped_count) + "개를 건너뛰었습니다.")  # 무시된 줄 개수를 사용자에게 안내

    except Exception as e:  # 파일을 만들거나 읽는 중 오류가 발생하면
        messagebox.showerror("파일 읽기 오류", "저장된 일정 파일을 불러오는 중 오류가 발생했습니다.\n" + str(e))  # 오류 내용을 메시지창으로 출력


def save_schedules():
    temp_file_name = file_name + ".tmp"  # 저장 중 오류가 나도 원본 파일을 최대한 보호하기 위한 임시 파일 이름 생성

    try:  # 파일 저장 과정에서 오류가 날 가능성을 대비
        with open(temp_file_name, "w", encoding="utf-8") as f:  # 먼저 임시 파일을 쓰기모드로 열어 안전하게 기록
            for s in schedules:  # 전체 일정 리스트 schedules 상자로부터 데이터를 하나씩 꺼내 변수 s에 대입하며 반복
                if is_valid_schedule_row(s):  # 만약 꺼낸 일정 리스트 s가 올바른 일정 규칙 검사를 통과한다면
                    f.write("|".join(s) + "\n")  # 리스트 내 요소들을 파이프 기호 문자열로 조립 결합하여 텍스트 파일에 쓰고 줄바꿈 처리

        os.replace(temp_file_name, file_name)  # 임시 파일 저장이 완전히 끝난 뒤 원본 파일로 교체하여 저장 중 파일 손상 가능성을 줄임
        return True  # 저장이 정상적으로 끝났음을 참으로 반환

    except Exception as e:  # 파일 저장 중 오류가 발생하면
        if os.path.exists(temp_file_name):  # 만약 실패 과정에서 임시 파일이 남아 있다면
            try:  # 임시 파일 삭제 중 오류가 날 가능성을 대비
                os.remove(temp_file_name)  # 실패한 임시 파일을 삭제
            except Exception:  # 임시 파일 삭제까지 실패하더라도 프로그램 전체가 멈추지 않게 처리
                pass  # 추가 처리 없이 조용히 넘어감
        messagebox.showerror("파일 저장 오류", "일정 파일을 저장하는 중 오류가 발생했습니다.\n" + str(e))  # 오류 내용을 메시지창으로 출력
        return False  # 저장이 실패했음을 거짓으로 반환


def update_status():
    today = str(datetime.date.today())  # 현재 시점 오늘 날짜를 YYYY-MM-DD 문자열로 변환해 변수 today에 저장
    today_count = sum(1 for s in schedules if s[1] <= today <= s[2])  # 시작일과 종료일 사이에 오늘 날짜가 포함되는 일정 개수를 합산해 변수 today_count에 저장
    status_label["text"] = f"등록 일정: {len(schedules)}개 | 화면 표시: {len(current_rows)}개 | 오늘 일정: {today_count}개 | 오늘 날짜: {today}"  # 조립 완료된 현황판 가독 문구로 화면 라벨 속성 최신화 교체 고침 설정


def show_rows(rows, empty_msg, dday_mode):
    current_rows.clear()  # 현재 화면 표시용 일정 데이터 목록 보관소 리스트 내용을 완전히 비움 리셋
    result_box.delete(0, tk.END)  # 결과창 리스트박스에 출력 중이던 기존 항목 문장들을 0번부터 끝까지 통째로 삭제 소거

    if len(rows) == 0:  # 만약 화면 표시 리스트 rows의 요소 개수가 == 0 이면
        result_box.insert(tk.END, empty_msg)  # 전체일정표시창에 빈 상태 예외 안내문구 글자 항목을 삽입 띄움
    else:  # 만약 출력할 일정 데이터 행이 하나 이상 엄연히 실존한다면
        for i, s in enumerate(rows, 1):  # rows 일정 목록 주머니로부터 아이템을 꺼내 1번 넘버링 i와 데이터 s 세트로 루프 가동 반복
            current_rows.append(s)  # 전역 연동 추적 바구니인 current_rows 리스트의 맨 뒤에 현재 노출할 일정 행 s 데이터를 차곡차곡 추가 담기

            task = s[0]  # 개별 일정 행 리스트의 0번째 요소를 일정 할일 명칭 변수 task에 지정
            start_date = s[1]  # 개별 일정 행 리스트의 1번째 요소를 일정 시작일 변수 start_date에 지정
            end_date = s[2]  # 개별 일정 행 리스트의 2번째 요소를 일정 종료일 변수 end_date에 지정
            priority = s[3]  # 개별 일정 행 리스트의 3번째 요소를 일정 우선순위 등급 변수 priority에 지정
            memo = s[4]  # 개별 일정 행 리스트의 4번째 요소를 일정 서브메모 변수 memo에 지정

            date_display = start_date if start_date == end_date else f"{start_date} ~ {end_date}"  # 시작일과 종료일이 같으면 하나만 표기하고 다르면 물결표로 연결해 변수 date_display에 저장
            dday = f"{make_dday_text(end_date)} | " if dday_mode else ""  # 만약 디데이 모드가 참이면 계산된 디데이 문자열을 넣고 아니면 빈 문자열을 변수 dday에 지정
            memo_part = f" | 메모: {memo}" if memo != "" else ""  # 만약 메모 내용이 빈칸 상태가 아니면 메모 표기 문자열을 넣고 아니면 빈 문자열을 변수 memo_part에 지정

            text = f"{i}. {date_display} | {dday}[{priority}] | {task}{memo_part}"  # 리스트박스 화면 각 줄 규격에 들어맞는 가독성 넘버링 포맷 문장을 조립 완성하여 변수 text에 저장
            result_box.insert(tk.END, text)  # 메인 결과창 리스트박스 위젯 항목의 맨 마지막 줄 위치 자리에 정밀 조립이 끝난 텍스트 문장을 정식 삽입 등록

    update_status()  # 리스트박스 화면 드로잉 연동 업무가 종결되었으므로 중앙 상황판 라벨 현황 정보 수치를 실시간 최신화 동기화 고침


def set_main_dates(start_str, end_str):
    entry_start.delete(0, tk.END)  # 메인 시작일 글자 입력창 칸에 쓰여있던 텍스트 데이터를 깨끗하게 삭제 새로고침
    entry_start.insert(0, start_str)  # 삭제 완료된 시작일 입력창 칸에 전달받은 시작일 문자열 start_str을 새로 채움 주입

    entry_end.delete(0, tk.END)  # 메인 종료일 글자 입력창 칸에 쓰여있던 텍스트 데이터를 깨끗하게 삭제 새로고침
    entry_end.insert(0, end_str)  # 삭제 완료된 종료일 입력창 칸에 전달받은 종료일 문자열 end_str을 새로 채움 주입


def clear_input_fields():
    entry_task.delete(0, tk.END)  # 할일 글자 입력창 칸에 쓰여있던 텍스트 데이터를 0번 위치부터 끝까지 깨끗하게 삭제 새로고침
    today_str = str(datetime.date.today())  # 현재 실시간 오늘 날짜를 YYYY-MM-DD 문자열로 변환해 변수 today_str에 저장
    set_main_dates(today_str, today_str)  # 날짜 설정 함수를 호출해 시작일과 종료일 입력창 모두 오늘 날짜로 자동 초기화 채움 주입
    priority_var.set("보통")  # 우선순위 콤보 선택 변수의 상태 값을 기본 디폴트 기준인 "보통" 단계 명칭으로 설정 초기화 리셋
    entry_memo.delete(0, tk.END)  # 메모 글자 입력창 칸에 쓰여있던 텍스트 데이터를 0번 위치부터 끝까지 깨끗하게 삭제 새로고침


def read_input_schedule():
    task = entry_task.get().strip()  # 할일 입력 글자 상자 컴포넌트로부터 문자열을 읽어와 양쪽 여백 공백 요소를 도려내 변수 task에 저장
    start_date = entry_start.get().strip()  # 시작일 입력 글자 상자 컴포넌트로부터 문자열을 읽어와 양쪽 여백 공백 요소를 도려내 변수 start_date에 저장
    end_date = entry_end.get().strip()  # 종료일 입력 글자 상자 컴포넌트로부터 문자열을 읽어와 양쪽 여백 공백 요소를 도려내 변수 end_date에 저장
    priority = priority_var.get()  # 우선순위 옵션 드롭다운 장치로부터 현재 고정 선택된 단계 명칭 문자열 값을 읽어와 변수 priority에 저장
    memo = entry_memo.get().strip()  # 메모 입력 글자 상자 컴포넌트로부터 문자열을 읽어와 양쪽 여백 공백 요소를 도려내 변수 memo에 저장

    if task == "":  # 만약 공백 도려내기가 끝난 할일 명칭 변수 task 내부의 실체 알맹이가 == "" 빈칸 상태에 해당하면
        messagebox.showerror("입력오류", "할 일을 입력하세요.")  # 내용물 부재 안내 조작 경고 메시지 창을 화면 상판 위에 띄움
        return None  # 결격 사유 판정 즉시 불합격 처리를 위해 None 반환
    if has_forbidden_char(task) or has_forbidden_char(memo):  # 만약 할일 변수 내용이나 메모 변수 내용 안에 약속된 금지 기호 문자가 포함되어 있다면
        messagebox.showerror("입력오류", forbidden_char_message())  # 저장 파일 파손 예방용 금지 문자 경고 메시지 창을 화면 상판 위에 띄움
        return None  # 결격 사유 판정 즉시 불합격 처리를 위해 None 반환
    if not is_valid_date(start_date):  # 만약 시작일 변수 start_date에 들어있는 텍스트 형식이 온전한 날짜 검사 규칙 판정에 거짓 상태로 탈락한다면
        messagebox.showerror("입력 오류", "시작 " + date_error_message())  # 시작일 규격 이탈 가이드 안내 에러 메시지 창을 화면 위에 띄움
        return None  # 결격 사유 판정 즉시 불합격 처리를 위해 None 반환
    if not is_valid_date(end_date):  # 만약 종료일 변수 end_date에 들어있는 텍스트 형식이 온전한 날짜 검사 규칙 판정에 거짓 상태로 탈락한다면
        messagebox.showerror("입력 오류", "종료 " + date_error_message())  # 종료일 규격 이탈 가이드 안내 에러 메시지 창을 화면 위에 띄움
        return None  # 결격 사유 판정 즉시 불합격 처리를 위해 None 반환

    today = str(datetime.date.today())  # 현재 실시간 오늘 날짜를 문자열로 변환해 변수 today에 저장
    if start_date < today or end_date < today:  # 만약 시작일 문자열이나 종료일 문자열 시점이 오늘 날짜보다 과거 시점 날짜 상태가 맞는다면
        messagebox.showerror("입력 오류", "오늘 이전 날짜는 등록할 수 없습니다.")  # 타임머신 등록 오동작 차단 과거 일자 불가 경고창을 화면 위에 띄움
        return None  # 원천 봉쇄 탈락으로 None 반환

    if start_date > end_date:  # 만약 시작일 문자열 시점이 종료일 문자열 시점보다 > 크다면(논리적 모순 상태라면)
        messagebox.showerror("입력 오류", "종료일은 시작일보다 빠를 수 없습니다.")  # 기간 범위 모순 경고 메시지 창을 화면 위에 띄움
        return None  # 원천 봉쇄 탈락으로 None 반환
    if not valid_priority(priority):  # 만약 콤보 변수 priority에 포착된 명칭 단계가 허용 규격 범위 안에 속하는 정상 명칭이 아니라면
        messagebox.showerror("입력 오류", "올바른 우선순위를 선택하세요.")  # 유효성 이탈 안내 경고창을 화면 위에 띄움
        priority_var.set("보통")  # 변수 오염 회복 수호 조치를 위해 콤보 드롭다운 변수 상태 값을 기본 표준인 "보통" 단계로 강제 변경 설정
        return None  # 결격 사유 판정 즉시 불합격 처리를 위해 None 반환

    new_schedule = [task, start_date, end_date, priority, memo]  # 모든 정밀 관문 검사 필터링을 성공 통과한 온전한 5대 핵심 필드 리스트 데이터를 변수 new_schedule에 조립 생성

    if new_schedule in schedules:  # 만약 신규 조립된 일정 리스트 데이터가 기존 전역 저장소 바구니인 schedules 상자 안에 완벽 중복 포함되어 있다면
        messagebox.showerror("입력 오류", "이미 완전히 동일하게 등록된 일정이 있습니다.")  # 데이터 중복 충돌 차단 안내 경고창을 화면 위에 띄움
        return None  # 결격 사유 판정 즉시 불합격 처리를 위해 None 반환

    return new_schedule  # 모든 필터망을 무사 통과한 최종 신규 일정 리스트 데이터를 반환


def add_schedule():
    new_schedule = read_input_schedule()  # read_input_schedule 검사 도구를 구동시켜 최종 합격 반환받은 일정 데이터를 변수 new_schedule에 복사 대입 최신화
    if new_schedule is None:  # 만약 획득해온 검증 통과 데이터 객체 new_schedule의 실체 상태 알맹이가 == None 이라면
        return  # 등록 성사 불가능 상태이므로 아래 저장 파일 추가 실행 구역을 무시하고 함수 즉시 탈락 종료
    schedules.append(new_schedule)  # 메인 메모리 보관소 리스트인 schedules 주머니 상자 맨 뒤 빈 구역 자리에 합격 완료 새 일정 리스트 데이터를 쏙 추가 담기
    save_schedules()  # save_schedules 파일 기록 도구를 호출 가동하여 갱신 완료 상태 목록을 영구 하드디스크 파일에 동기화 저장
    clear_input_fields()  # clear_input_fields 화면 청소 함수를 가동 작동시켜 상판 입력 글자 칸 구성 단락들을 깨끗하게 디폴트 원위치 새로고침
    show_all()  # 신규 데이터가 반영 전개된 최신 목록 리스트 현황을 메인 결과창 리스트박스 뷰포트 영역 칸에 전체 보기 모드로 완벽 새로고침 리드로잉


def sort_key_by_date_priority(s):
    priority_order = {"긴급": 1, "높음": 2, "보통": 3, "낮음": 4}  # 우선순위 한글 명칭을 정수 스케일값으로 변환해 줄 사전 딕셔너리 priority_order 설정
    return (s[1], priority_order.get(s[3], 99))  # 1번째 요소인 시작날짜를 대장 조건으로, 3번째 요소인 우선순위 정수값을 서브 조건으로 정렬 튜플 세트를 반환


def sort_key_by_priority_date(s):
    priority_order = {"긴급": 1, "높음": 2, "보통": 3, "낮음": 4}  # 우선순위 한글 명칭을 정수 스케일값으로 변환해 줄 사전 딕셔너리 priority_order 설정
    return (priority_order.get(s[3], 99), s[1])  # 3번째 요소인 우선순위 정수 단계를 대장 조건으로, 1번째 요소인 시작날짜를 서브 조건으로 정렬 튜플 세트를 반환


def show_all():
    sorted_rows = sorted(schedules, key=sort_key_by_date_priority)  # 전체 저장소 리스트 schedules 데이터를 시작일 상위, 우선순위 하위 규칙에 맞춰 오름차순 정렬해 변수 sorted_rows에 저장
    show_rows(sorted_rows, "등록된 일정이 없습니다.", False)  # 정렬 완성된 리스트 결과물 데이터를 화면 메인 뷰포트 리스트박스 상판에 정식 출력 등록


def sort_by_priority():
    sorted_rows = sorted(schedules, key=sort_key_by_priority_date)  # 전체 저장소 리스트 schedules 데이터를 우선순위 상위, 시작일 하위 규칙에 맞춰 정렬해 변수 sorted_rows에 저장
    show_rows(sorted_rows, "등록된 일정이 없습니다.", False)  # 우선순위 정렬 기준으로 정제 완료된 결과를 결과창에 최종 정식 출력


def open_date_input_window(title, guide_text, button_text, dday_mode):
    win = tk.Toplevel(root)  # 메인 창 레이어 계층 위에 독립으로 동동 뜨는 보조 윈도우 팝업창을 객체화해 win 변수에 저장
    win.title(title)  # 보조 윈도우 팝업창 win의 상단 윈도우 제목 명칭 글자를 주입 매개변수 값인 title 내용으로 변경 설정
    win.geometry("360x170")  # 보조 윈도우 팝업창 win의 화면 폼 레이아웃 크기를 가로 360, 세로 170 수치 규격 크기로 정밀 설정
    win.resizable(False, False)  # 사용자가 임의로 보조 마우스 조작을 통해 크기를 조절할 수 없도록 가변 변경 불가능하게 고정 설정

    tk.Label(win, text=guide_text, font=("Arial", 11, "bold")).pack(pady=8)  # 안내문 문자 라벨 컴포넌트를 위아래 적절한 여백 설정해 보조창 상단에 정렬 배치
    tk.Label(win, text="형식: YYYY-MM-DD  예: 2026-05-11").pack()  # 날짜 양식 예시 안내문 문자 라벨 컴포넌트를 서브 하단 자리에 정렬 패킹 배치

    date_entry = tk.Entry(win, width=22, justify="center")  # 날짜 글자를 타이핑 입력받을 텍스트 입력창 컴포넌트를 중앙 정렬 속성 주어 생성 후 date_entry 변수에 저장
    date_entry.pack(pady=8)  # 보조창 전용 글자 입력창 date_entry 위젯을 위아래 바깥 여백 8 수치 부여해 정렬 배치
    date_entry.insert(0, str(datetime.date.today()))  # 타이핑 수고를 덜어주기 위해 보조창 글자 입력창 칸 내부에 실시간 현재 컴퓨터 기준의 오늘 날짜 YYYY-MM-DD 문자열을 선제 디폴트 주입 채움

    def run():  # 보조 팝업창 내부의 기능 실행 단추를 마우스 클릭 딸컥 했을 때 실제 결과 처리를 작동시키는 핵심 제어 내부 함수 정의
        target_date = date_entry.get().strip()  # 보조창 전용 글자 입력창 칸으로부터 글자를 읽어와 양쪽 끝자락 여백 공백 요소를 도려낸 타깃 날짜 텍스트를 변수 target_date에 저장

        if not is_valid_date(target_date):  # 만약 획득한 타깃 날짜 문자열 변수 내용이 진짜 날짜 유효 조건 판정 함수를 거쳐 거짓 상태로 탈락 깨져있다면
            messagebox.showerror("입력 오류", date_error_message(), parent=win)  # 오입력 안내 경고 메시지 창을 메인이 아닌 현재 보조 팝업 창 win 위에 최우선으로 띄움
            return  # 하단 검색 필터 구역 진입을 차단하고 내부 함수 구동 즉시 중단 종료 빠져나감

        filtered = [s for s in schedules if s[1] <= target_date <= s[2]]  # 전체 일정 목록에서 시작일과 종료일 기간 범위 안에 타깃 날짜 target_date가 속하는 일정만 필터링 전개해 리스트 filtered에 저장
        sorted_filtered = sorted(filtered, key=sort_key_by_date_priority)  # 날짜상위 정렬 기준 규칙에 동기화시켜 필터 조회 결과 목록들을 시간순 오름차순으로 완벽 정렬해 sorted_filtered에 저장

        show_rows(sorted_filtered, "해당 날짜에 포함되는 일정이 없습니다.", dday_mode)  # 필터 요건 정제가 완료된 최종 일정 목록 세트를 메인 화면 결과창 리스트박스 뷰포트 영역에 정식 출력 표출
        win.destroy()  # 수색 조회 필터 전달 목적 임무가 깔끔히 성사 종결되었으므로 임시 가동 보조 팝업창 win 컴포넌트를 완전히 파괴 닫음

    tk.Button(win, text=button_text, width=12, command=run).pack(pady=5)  # 보조 입력 팝업창의 하단 기능 실행 단추 컴포넌트를 명세서 글자 타이틀과 연결하고 클릭 시 내부 run 함수를 가동시키도록 연동 바인딩하여 팩 배치 정렬


def open_date_search_window():
    open_date_input_window("날짜별 조회", "조회할 날짜를 입력하세요.", "조회", False)  # 디데이 가독 문구 출력 기능을 무효(False) 모드로 고정 설정 지정하여 날짜별 조회 전용 보조창 가동 함수를 호출 구동


def open_dday_window():
    open_date_input_window("D-day 조회", "D-day를 확인할 날짜를 입력하세요.", "조회", True)  # 디데이 가독 문구 출력 기능을 활성화(True) 모드로 고정 설정 지정하여 디데이 계산 전용 보조창 가동 함수를 호출 구동


def export_to_csv():
    if len(schedules) == 0:  # 만약 전역 메모리 보관소 리스트인 schedules의 요소 개수가 == 0 상태로 텅 비어있다면
        messagebox.showerror("CSV 저장 오류", "저장할 일정이 없습니다.")  # 데이터 부재 안내 조작 경고 메시지 창을 화면 위에 띄움
        return  # CSV 파일 저장 가동 로직 구역 진입을 차단하고 함수 구동 즉시 중단 종료

    csv_file = filedialog.asksaveasfilename(
        title="CSV 파일 저장 위치 선택",
        defaultextension=".csv",
        filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")],
        initialfile="schedules.csv"
    )  # 사용자가 CSV 파일을 저장할 위치와 파일명을 직접 선택하게 함

    if csv_file == "":  # 만약 사용자가 저장 위치 선택창에서 취소를 눌렀다면
        return  # CSV 저장 작업을 중단

    try:  # CSV 파일 생성 및 쓰기 작업 도중 외부 시스템 권한 문제 등으로 터질 수 있는 에러 예외 감시 시도
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:  # 한글 깨짐 현상을 방지하는 utf-8-sig 인코딩 규격으로 CSV 파일을 쓰기모드로 생성해 엶
            writer = csv.writer(f)  # 파이썬 표준 csv 도구를 불러와 해당 파일 스트림 f에 데이터를 써 내려갈 writer 객체를 생성 연결
            writer.writerow(["할 일", "시작일", "종료일", "우선순위", "메모"])  # CSV 파일의 최상단 첫 번째 줄에 분류 항목 타이틀 헤더 행을 정식 작성 삽입 기록

            sorted_schedules = sorted(schedules, key=sort_key_by_date_priority)  # 시간 순서의 가독성을 높이기 위해 전체 일정 데이터를 시작일 기준 오름차순 정렬하여 변수 sorted_schedules에 저장
            for s in sorted_schedules:  # 오름차순 정렬 완료된 일정 리스트 주머니 상자로부터 데이터를 하나씩 꺼내 변수 s에 대입하며 루프 수행 반복
                writer.writerow(s)  # 꺼내온 일정 리스트 행 s 데이터를 CSV 파일의 한 행 텍스트 줄글로 기록 저장

        answer = messagebox.askyesno("CSV 저장 완료", "CSV 파일이 저장되었습니다.\n지금 열어보시겠습니까?")  # 저장된 파일을 바로 열어볼지 사용자에게 물어봄

        if answer:  # 만약 사용자가 예를 누르면
            try:  # 파일 열기 과정에서 오류가 날 가능성을 대비
                if hasattr(os, "startfile"):  # 윈도우 환경에서 os.startfile 사용 가능 여부를 확인
                    os.startfile(csv_file)  # 윈도우 기본 연결 프로그램으로 CSV 파일 열기
                else:  # 만약 현재 운영체제에서 os.startfile을 지원하지 않는다면
                    messagebox.showinfo("파일 열기 안내", "CSV 파일은 저장되었지만 이 운영체제에서는 자동 열기를 지원하지 않습니다.\n저장 위치에서 직접 열어주세요.")  # 직접 열기 안내
            except Exception as e:  # 만약 파일 열기 중 오류가 발생하면
                messagebox.showerror("파일 열기 오류", "CSV 파일은 저장되었지만 자동으로 열지 못했습니다.\n" + str(e))  # 파일 열기 실패 안내창 출력

    except Exception as e:  # 만약 CSV 저장 과정에서 오류가 발생하면
        messagebox.showerror("CSV 저장 오류", "CSV 파일 저장 중 오류가 발생했습니다.\n" + str(e))  # 저장 실패 오류창 출력


def delete_selected():
    selected = result_box.curselection()  # 전체 결과창 리스트박스 위젯 상판에서 사용자가 마우스 클릭 선택 마킹한 아이템의 고유 순서 위치 번호를 퍼와 변수 selected에 저장
    if len(selected) == 0:  # 만약 사용자가 메인 결과창 리스트박스 영역 항목을 아무것도 고르지 않아 고유 번호 목록의 개수가 == 0 이라면
        messagebox.showerror("선택 오류", "삭제할 일정을 먼저 선택하세요.")  # 조작 타깃 실종 예외 알림 메시지 경고창을 화면 위에 즉시 노출 띄움
        return  # 후속 파일 영구 삭제 제거 연동 로직 단계 진입을 막기 위해 함수 실행 동작을 즉시 중단 종료 빠져나감

    index = selected[0]  # 다중 선택 클릭 혼선 오동작 방지 규격 안전장치에 의거해 기 고른 목록 순번 중 가장 선두의 첫 번째 행 상수 번호를 변수 index에 대입 저장
    if index >= len(current_rows):  # 만약 매칭 타깃 위치 인덱스 번호인 변수 index 숫자가 현재 활성 표출 화면용 리스트 주머니 크기 범위를 일탈해 넘어서면
        messagebox.showerror("삭제 오류", "삭제할 일정이 없습니다.")  # 맵핑 일치 실패 에러 안내 경고 메시지 창을 화면 위에 노출 띄움
        return  # 후속 파일 영구 삭제 제거 연동 로직 단계 진입을 막기 위해 함수 실행 동작을 즉시 중단 종료 빠져나감

    target = current_rows[index]  # 현재 매칭 싱크 번호인 index 순서에 해당하는 화면 표시용 타깃 일정 리스트 데이터를 삭제 제거 타깃 변수 target에 지정 저장
    if target in schedules:  # 만약 최종 맵핑 성사 완료된 실제 타깃 일정 리스트 데이터가 전체 일정 데이터베이스인 schedules 리스트 주머니 안에 온전히 들어있다면
        schedules.remove(target)  # 메인 메모리 보관소 변수인 schedules 리스트 바구니 상자 내부 공간에서 해당 타깃 일정 데이터를 영구 삭제 제거 소거
        save_schedules()  # save_schedules 파일 세이브 도구를 가동하여 변경 완료 상태 목록을 영구 하드디스크 텍스트 파일에 영구 동기화 저장
        show_all()  # 삭제 변경 결과가 전개 반영되도록 화면 메인 결과창 리스트박스 뷰포트 영역 칸 항목들을 전체 보기 모드로 새로고침 리드로잉
        result_box.selection_clear(0, tk.END)  # 삭제 이후 리스트박스에 잔존할 수 있는 기존 마우스 선택 포커스 활성화 표식을 모두 해제 투명화 클리어 처리
        messagebox.showinfo("삭제 완료", "선택한 일정이 삭제되었습니다.")  # 최종 성공 완료 알림 팝업창을 화면 위에 정식 노출 띄움
    else:  # 만약 화면 타깃 일정을 메인 데이터베이스 저장소 안에서 끝내 스캔 매칭해 찾아내지 못했다면
        messagebox.showerror("삭제 오류", "삭제할 일정을 찾지 못했습니다.")  # 삭제 실패 오류 알림 에러창을 화면 위에 노출 띄움


def edit_selected():
    selected = result_box.curselection()  # 전체 결과창 리스트박스 위젯에서 사용자가 마우스 클릭 마킹한 아이템의 고유 순서 위치 번호를 퍼와 변수 selected에 저장
    if len(selected) == 0:  # 만약 사용자가 메인 결과창 영역 항목을 아무것도 고르지 않아 고유 번호 목록 개수가 == 0 상태라면
        messagebox.showerror("선택 오류", "수정할 일정을 먼저 선택하세요.")  # 수정 조작 타깃 부재 예외 알림 메시지 경고창을 화면 위에 즉시 노출 띄움
        return  # 후속 수정 정보 가공 절차 단계 진입을 막기 위해 함수 실행 동작을 즉시 중단 종료 빠져나감

    index = selected[0]  # 다중 클릭 혼선 방지 규격 안전장치에 따라 선택 목록 순번 중 가장 첫 번째 선두 행 상수 번호를 변수 index에 대입 저장
    if index >= len(current_rows):  # 만약 타깃 위치 인덱스 번호인 변수 index 숫자가 현재 활성 화면용 리스트 주머니 크기 범위를 일탈해 넘어서면
        messagebox.showerror("수정 오류", "수정할 일정이 없습니다.")  # 맵핑 일치 실패 에러 안내 경고 메시지 창을 화면 위에 노출 띄움
        return  # 후속 수정 정보 가공 절차 단계 진입을 막기 위해 함수 실행 동작을 즉시 중단 종료 빠져나감

    target = current_rows[index]  # 현재 매칭 싱크 번호인 index 순서에 짝 대응하는 화면 표시용 타깃 일정 리스트 데이터를 변경 교체 타깃 변수 target에 지정 저장
    if target not in schedules:  # 만약 맵핑 성사된 실제 타깃 일정 리스트 데이터 내용물이 메인 전체 일정 저장소 schedules 리스트 안에 실존하지 않는다면
        messagebox.showerror("수정 오류", "수정할 일정을 찾지 못했습니다.")  # 데이터 동기화 유실 에러 안내 경고창을 화면 위에 띄움
        return  # 후속 수정창 윈도우 빌딩 연동 페이즈 진입을 막고 함수 구동 즉시 중단 종료 빠져나감

    win = tk.Toplevel(root)  # 메인 root 창 레이어 계층 토대 위에 완벽 독립 레이어로 동동 뜨는 보조 수정 전용 윈도우 창 객체를 생성하여 변수 win에 저장
    win.title("일정 수정")  # 보조 수정 윈도우 창 win의 상단 윈도우 제목 명칭 글자를 "일정 수정" 이름표로 설정
    win.geometry("460x280")  # 수려하고 가독성 높은 조작 환경 제공 차원에서 범용 수정 창의 화면 폼 레이아웃 크기를 가로 460, 세로 280 수치 규격 크기로 정밀 조정 설정
    win.resizable(False, False)  # 사용자가 임의로 보조 창의 모서리를 마우스 드래그해 크기를 찌그러뜨릴 수 없도록 화면 크기 변경 가변 불가능 고정 설정

    frame = tk.Frame(win)  # 수정 컴포넌트 항목 이름표들과 글자 입력 위젯들을 단정하게 정렬해 가두어줄 빈 프레임 상자를 생성하여 변수 frame에 저장
    frame.pack(pady=15)  # 수정 항목 정렬 프레임 frame 상자를 위아래 바깥 여백 15 넉넉하게 설정해 본체 레이어 위에 정식 안착 배치

    tk.Label(frame, text="할 일").grid(row=0, column=0, padx=5, pady=5)  # 할일 안내라벨 컴포넌트를 격자 레이아웃의 0행 0열 자리에 정식 안착 배치
    edit_task = tk.Entry(frame, width=32)  # 수정한 새 할일 제목 글자를 키보드로 타이핑 입력받을 글자 입력창 위젯을 너비 32 크기로 생성해 변수 edit_task에 저장
    edit_task.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")  # 할일 수정 입력창 위젯을 열 병합 공간 확장 속성 주어 격자의 0행 1열 서쪽 좌측 정렬 자리에 배치
    edit_task.insert(0, target[0])  # 할일 글자 입력창 칸 표면 맨 앞단 자리에 고치기 전 과거 상태 타깃 기존 일정의 0번째 요소 할일 명칭 데이터를 자동으로 미리 삽입 채워 넣음

    tk.Label(frame, text="시작일").grid(row=1, column=0, padx=5, pady=5)  # 시작일 안내라벨 컴포넌트를 격자 레이아웃의 1행 0열 자리에 정식 안착 배치
    edit_start = tk.Entry(frame, width=15)  # 수정한 새 시작일 일자 글자를 입력받을 글자 입력창 컴포넌트를 너비 15 크기로 생성해 변수 edit_start에 저장
    edit_start.grid(row=1, column=1, padx=5, pady=5, sticky="w")  # 시작일 수정 입력창 위젯을 격자 레이아웃의 1행 1열 서쪽 좌측 정렬 자리에 정식 배치
    edit_start.insert(0, target[1])  # 시작일 글자 입력창 칸 표면 맨 앞단 자리에 과거 상태 타깃 기존 일정의 1번째 요소 시작일 문자열 데이터를 자동으로 미리 삽입 채워 넣음

    tk.Label(frame, text="종료일").grid(row=2, column=0, padx=5, pady=5)  # 종료일 안내라벨 컴포넌트를 격자 레이아웃의 2행 0열 자리에 정식 안착 배치
    edit_end = tk.Entry(frame, width=15)  # 수정한 새 종료일 일자 글자를 입력받을 글자 입력창 컴포넌트를 너비 15 크기로 생성해 변수 edit_end에 저장
    edit_end.grid(row=2, column=1, padx=5, pady=5, sticky="w")  # 종료일 수정 입력창 위젯을 격자 레이아웃의 2행 1열 서쪽 좌측 정렬 자리에 정식 배치
    edit_end.insert(0, target[2])  # 종료일 글자 입력창 칸 표면 맨 앞단 자리에 과거 상태 타깃 기존 일정의 2번째 요소 종료일 문자열 데이터를 자동으로 미리 삽입 채워 넣음


    tk.Label(frame, text="우선순위").grid(row=3, column=0, padx=5, pady=5)  # 우선순위 안내라벨 컴포넌트를 격자 레이아웃의 3행 0열 자리에 정식 안착 배치
    edit_priority_var = tk.StringVar(value=target[3])  # 수정 폼 화면 내부 콤보 옵션 메뉴 드롭다운의 선택 동작을 실시간 지탱할 문자 변수를 생성하고 고치기 전 기존 일정의 3번째 요소 등급 명칭 값으로 초기 대입 세팅해 저장
    tk.OptionMenu(frame, edit_priority_var, "긴급", "높음", "보통", "낮음").grid(row=3, column=1, padx=5, pady=5, sticky="w")  # 우선순위 선택 드롭다운 옵션 메뉴 장치를 생성해 서쪽 좌측 정렬 속성 주어 격자의 3행 1열 자리에 정식 안착 배치

    tk.Label(frame, text="메모").grid(row=4, column=0, padx=5, pady=5)  # 메모 안내라벨 컴포넌트를 격자 레이아웃의 4행 0열 자리에 정식 안착 배치
    edit_memo = tk.Entry(frame, width=32)  # 수정한 새 서브메모 텍스트 글자를 키보드로 입력받을 글자 입력창 컴포넌트를 너비 32 크기로 생성하여 변수 edit_memo에 저장
    edit_memo.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="w")  # 메모 수정 입력창 위젯을 열 병합 공간 확장 속성 주어 격자의 4행 1열 서쪽 좌측 정렬 자리에 정식 안착 배치
    edit_memo.insert(0, target[4])  # 메모 글자 입력창 칸 표면 맨 앞단 자리에 고치기 전 과거 상태 타깃 기존 일정의 4번째 요소 메모 텍스트 문자열 내용을 자동으로 미리 삽입 채워 넣음

    def save_edit():  # 수정 보조창 화면 내부 맨 하단 구역의 최종 '저장' 버튼 단추를 유저가 마우스 클릭했을 때 실제 데이터 영구 덮어쓰기 변경 처리해 주는 핵심 제어 내부 함수 정의
        task = edit_task.get().strip()  # 할일 글자 입력창 칸 위젯으로부터 데이터를 읽어와 양쪽 끝자락 공백 단락을 도려낸 순수 알맹이 문자열을 변수 task에 저장
        start_date = edit_start.get().strip()  # 시작일 글자 입력창 칸 위젯으로부터 데이터를 읽어와 양쪽 끝자락 공백 단락을 도려낸 순수 알맹이 문자열을 변수 start_date에 저장
        end_date = edit_end.get().strip()  # 종료일 글자 입력창 칸 위젯으로부터 데이터를 읽어와 양쪽 끝자락 공백 단락을 도려낸 순수 알맹이 문자열을 변수 end_date에 저장
        priority = edit_priority_var.get()  # 옵션 드롭다운 메뉴 콤보 박스 장치로부터 유저가 최종 마우스 선택 마킹한 우선순위 문자열 명칭 단락 값을 읽어와 변수 priority에 저장
        memo = edit_memo.get().strip()  # 메모 글자 입력창 칸 위젯으로부터 데이터를 읽어와 양쪽 끝자락 공백 단락을 도려낸 순수 알맹이 문자열을 변수 memo에 저장

        if task == "":  # 만약 공백 제거 완료된 할일 제목 변수 task 내부 알맹이 글자 내용이 == "" 빈칸 상태에 해당하면
            messagebox.showerror("입력 오류", "할 일을 입력하세요.", parent=win)  # 입력 내용물 결격 가이드 경고창을 메인이 아닌 현재 수정 보조 윈도우 창 win 위에 최우선으로 노출 출력
            return  # 비정상 데이터 조건 상황이므로 후속 하드디스크 저장 연동 페이즈 진입을 즉시 전면 차단하고 내부 함수 구동 즉시 중단 종료 빠져나감
        if has_forbidden_char(task) or has_forbidden_char(memo):  # 만약 수정 기재 입력한 할일 명칭 내용이나 서브메모 명칭 내용 문자열 내부에 파일 파손 유발 금지 기호 문자가 섞여 포함되어 있다면
            messagebox.showerror("입력 오류", forbidden_char_message(), parent=win)  # 금지 문자 사용 경고 에러 메시지창을 수정 보조 윈도우 창 win 위에 최우선으로 노출 출력
            return  # 비정상 데이터 조건 상황이므로 후속 하드디스크 저장 연동 페이즈 진입을 즉시 전면 차단하고 내부 함수 구동 즉시 중단 종료 빠져나감
        if not is_valid_date(start_date):  # 만약 새로 적어 기재한 시작일 문자열 데이터 형식이 날짜 정밀 검사 규칙 관문에 거짓 상태로 탈락한다면
            messagebox.showerror("입력 오류", "시작 " + date_error_message(), parent=win)  # 시작일 형식 요건 이탈 경고 에러창을 수정 보조 윈도우 창 win 위에 최우선 노출 출력
            return  # 비정상 데이터 조건 상황이므로 후속 하드디스크 저장 연동 페이즈 진입을 즉시 전면 차단하고 내부 함수 구동 즉시 중단 종료 빠져나감
        if not is_valid_date(end_date):  # 만약 새로 적어 기재한 종료일 문자열 데이터 형식이 날짜 정밀 검사 규칙 관문에 거짓 상태로 탈락한다면
            messagebox.showerror("입력 오류", "종료 " + date_error_message(), parent=win)  # 종료일 형식 요건 이탈 경고 에러창을 수정 보조 윈도우 창 win 위에 최우선 노출 출력
            return  # 비정상 데이터 조건 상황이므로 후속 하드디스크 저장 연동 페이즈 진입을 즉시 전면 차단하고 내부 함수 구동 즉시 중단 종료 빠져나감

        today = str(datetime.date.today())  # 현재 실시간 컴퓨터 기준 오늘 날짜를 문자열로 변환 연산해 변수 today에 저장
        if start_date < today or end_date < today:  # 만약 수정 입력한 시작일 문자열이나 종료일 문자열 시점이 오늘 날짜보다 < 작다면 (이미 지나가 버린 과거 모순 상황이라면)
            messagebox.showerror("입력 오류", "오늘 이전 날짜는 등록할 수 없습니다.", parent=win)  # 타임머신 조작 금지 과거 일자 불가 경고창을 수정 보조 창 win 위에 노출 띄움
            return  # 비정상 데이터 조건 상황이므로 후속 하드디스크 저장 연동 페이즈 진입을 즉시 전면 차단하고 내부 함수 구동 즉시 중단 종료 빠져나감

        if start_date > end_date:  # 만약 수정 시작일 시점이 수정 종료일 시점보다 > 크다면 (시작이 끝보다 미래인 역전 논리적 모순 범위 상황이라면)
            messagebox.showerror("입력 오류", "종료일은 시작일보다 빠를 수 없습니다.", parent=win)  # 범위 역전 모순 에러 경고창을 수정 보조 윈도우 창 win 위에 최우선 노출 출력
            return  # 비정상 데이터 조건 상황이므로 후속 하드디스크 저장 연동 페이즈 진입을 즉시 전면 차단하고 내부 함수 구동 즉시 중단 종료 빠져나감
        if not valid_priority(priority):  # 만약 콤보 옵션 변수 priority 상자 안에 들어온 우선순위 명칭이 규정 단계 허용 튜플 범위 안에 속하는 정상 명칭이 아니라면
            messagebox.showerror("입력 오류", "올바른 우선순위를 선택하세요.", parent=win)  # 우선순위 규격 이탈 경고 에러창을 수정 보조 윈도우 창 win 위에 최우선 노출 출력
            return  # 비정상 데이터 조건 상황이므로 후속 하드디스크 저장 연동 페이즈 진입을 즉시 전면 차단하고 내부 함수 구동 즉시 중단 종료 빠져나감

        new_item = [task, start_date, end_date, priority, memo]  # 모든 까다로운 검사 필터링을 성공 통과한 새로이 입력받은 수정 데이터 알맹이 구성 성분값들을 정렬 결합해 새 일반 일정 리스트 new_item 데이터 내용으로 신규 조립 완료

        if new_item != target and new_item in schedules:  # 만약 새로이 바꾼 일정 데이터 내용물이 과거 타깃 데이터 내용과 분명히 다르면서 정작 이미 schedules 데이터베이스 안에 똑같이 중복 존재한다면
            messagebox.showerror("입력 오류", "이미 완전히 동일하게 등록된 일정이 있습니다.", parent=win)  # 중복 데이터 충돌 수정 등록 거부 팝업 에러창을 수정 보조 윈도우 창 win 위에 출력
            return  # 충돌 데이터 비상 상황이므로 후속 세이브 로직 작동을 전면 차단 내부 함수 구동 즉시 중단 종료 빠져나감
        if target not in schedules:  # 만약 맵핑 추적 확보해온 수정 전 과거 타깃 원본 행 데이터가 메인 메모리 저장소 변수인 schedules 리스트 바구니 상자 내부 공간 안에 온전하게 들어 실존하지 않는다면
            messagebox.showerror("수정 오류", "수정할 일정을 찾지 못했습니다.", parent=win)  # 매칭 정보 증발 실종 에러 안내 팝업창을 수정 보조 윈도우 창 win 위에 최우선 출력
            return  # 매칭 유실 비상 상황이므로 후속 세이브 로직 작동을 전면 차단 내부 함수 구동 즉시 중단 종료 빠져나감

        idx = schedules.index(target)  # 메인 데이터베이스 리스트 schedules 구조 안에서 과거 원본 타깃 데이터 target이 위치해 보존된 고유 순서 인덱스 자릿수 번호를 정밀 스캔 탐색하여 변수 idx에 저장
        schedules[idx] = new_item  # 발견해낸 해당 변수 idx 순번 위치 자리를 통째로 수정한 새 리스트 new_item 완성형 데이터 알맹이 내용으로 완벽 덮어써서 갱신 교체 최신화 업데이트

        save_schedules()  # 앞서 작성 설계한 파일 영구 세이브 도구 함수 save_schedules를 가동 작동시켜 메모리 덮어쓰기 갱신 완료 상태 목록 결과를 영구 텍스트 파일 저장소에 즉시 동기화 세이브 저장
        show_all()  # 앞서 작성 설계한 전체 보기 화면 드로잉 함수 show_all을 연동 호출 가동시켜 화면 메인 결과창 리스트박스 뷰포트 목록 화면을 최신화 새로고침 정렬 고침 노출
        win.destroy()  # 모든 유효 데이터 정밀 수정 덮어쓰기 변경 및 연쇄 팝업 화면 동기화 저장 처리 연동 작업이 완벽 성사 끝났으므로 가동 완료된 수정 보조 윈도우 창 win 컴포넌트 객체를 완전히 삭제 파괴 닫음
        messagebox.showinfo("수정 완료", "일정이 수정되었습니다.")  # 정상 갱신 변경 성공 성사 인지용 최종 완료 알림 질문창을 화면 위에 정식 노출 출력 띄움

    tk.Button(win, text="저장", width=12, command=save_edit).pack(pady=5)  # 범용 수정 보조창 화면 내부 맨 하단 구역에 유효 데이터 영구 저장 갱신 임무를 실제 수행할 '저장' 버튼 단추 위젯을 생성하고 내부 save_edit 함수와 바인딩 연동해 팩 정렬 안착 배치


def reset_all_schedules():
    if messagebox.askyesno("초기화 확인", "등록된 모든 일정을 삭제하시겠습니까?"):  # 유저 복구 불가능 실수 낙하 오작동 방지 안전 확인 차원에서 전체 삭제 동의 의사를 질문 팝업창으로 띄워 안전 확인하고 만약 '예' 판정 동의가 떨어지면
        schedules.clear()  # 모든 일정 데이터가 누적 적재되어 보관 중이던 전역 메인 메모리 변수 schedules 리스트 주머니 상자 내부의 알맹이 내용물들을 흔적도 없이 완전히 포맷 통째로 지워버려 포맷 리셋 초기화 삭제
        current_rows.clear()  # 현재 화면 메인 결과창 뷰포트 상판에 출력 노출 중인 가상 전개 매칭 일정 데이터 목록 리스트인 current_rows 내부 내용물도 통째로 삭제 소거 리셋
        save_schedules()  # 텅 비워져 완전 클리어 리셋된 빈 껍데기 전체 일정 리스트 상태 결과를 save_schedules 파일 세이브 도구 함수를 가동시켜 하드디스크 텍스트 파일 영구 저장소에 덮어써서 동기화 저장
        clear_input_fields()  # clear_input_fields 화면 글자 칸 청소 함수를 연동 호출 구동시켜 메인 상판에 유저가 적어 두었던 입력칸 구성 단락 글자들을 모두 깨끗하게 디폴트 포맷 원위치 새로고침 지움
        show_all()  # 완전 포맷 삭제 소거 초기화 처리 결과가 시각적으로 전개 즉시 반영되도록 화면 메인 결과창 리스트박스 위젯 목록 화면을 전체 보기 백지 모드로 완벽 최신화 새로고침 리드로잉


def show_date_chart():
    if len(schedules) == 0:  # 만약 메인 활성 메모리 저장소 변수인 schedules 데이터베이스 리스트 주머니 상자 안에 담긴 데이터 요소 개수가 == 0 상태로 완전히 텅 비어있다면
        messagebox.showerror("시각화 오류", "시각화할 일정이 없습니다.")  # 데이터 부재 안내 시각화 불가 조작 오류 에러 메시지 경고창을 메인 화면 창 상판 위에 즉시 노출 띄움
        return  # 차트 드로잉 연산 수행이 절대 불가능한 무산 상황이므로 후속 시각화 구동 가동 경로 진입을 원천 차단하고 함수 구동 실행을 즉시 중단 종료 빠져나감

    date_counts = {}  # 화면 차트에 그릴 가로축 특정 날짜 문자열 정보들을 검색 키로 삼고, 당일 겹치는 발생 중복 카운트 밀집도 정수 수치값을 밸류로 누적 합산 매칭해 기록해나갈 빈 집계 사전 딕셔너리 date_counts 상자 설정

    for s in schedules:  # 메인 보관소 전체 일정 데이터베이스인 schedules 주머니 상자로부터 온전한 일반 단발성 일정 리스트 데이터 묶음을 차례대로 하나씩 꺼내어 변수 s에 대입하며 루프 수행 가동 반복
        start_d = parse_date_str(s[1])  # 개별 일정 리스트 s의 1번째 구성 요소 위치에 기록 보존되어 박힌 스케줄 개시작 시작날짜 문자열 글자 정보를 빼내어 날짜 간 차감 비교 연산 도구를 위해 내부 날짜 객체 타입 구조로 파싱해 변수 start_d에 변환 저장
        end_d = parse_date_str(s[2])  # 개별 일정 리스트 s의 2번째 구성 요소 위치에 기록 보존되어 박힌 스케줄 마감 종료 기한 날짜 문자열 글자 정보를 빼내어 날짜 간 차감 비교 연산 도구를 위해 내부 날짜 객체 타입 구조로 파싱해 변수 end_d에 변환 저장
        days_count = (end_d - start_d).days + 1  # 파싱 변환해 온 두 날짜 객체의 순수 시점 빼기 차감 연산 뺄셈을 가동하여 추출해 낸 경과 일수 차이 값에 당일 포함 규칙 보정을 위한 1을 추가 가산 더해 이 일정이 총 며칠 동안이나 걸쳐 존재하는 스케줄인지 산출해 변수 days_count에 대입 저장

        if days_count > CHART_MAX_DAYS:  # 만약 산출 측정해낸 단일 스케줄의 지속 소요 차지 기간 일수 days_count 수치 결과가 사전에 정의 선언 세팅해둔 화면 무한 스크롤 다운 차단용 안전장치 상한 한계 기준치인 CHART_MAX_DAYS 일수(366일)보다 > 초과하여 크다면
            messagebox.showerror("시각화 오류", f"기간이 너무 긴 일정이 있어 시각화할 수 없습니다. 한 일정은 최대 {CHART_MAX_DAYS}일까지만 시각화할 수 있습니다.")  # 메모리 붕괴 폭발 및 시스템 무한 루프 멈춤 에러 예방 차원에서 위험 감지 시각화 중단 안내 경고 메시지 창을 화면에 안전 팝업 출력 노출
            return  # 위험 데이터 포함 포착 상황이므로 차트 드로잉 연산 수행 구동을 즉시 파기 전면 중단 차단하고 함수 실행을 곧바로 종료 빠져나감

        curr_d = start_d  # 안전 검증 필터를 무사 통과한 정상 일정을 하루하루 쪼개어 차트 카운트 장부 사전에 누적 집계 기록해나가기 위한 날짜 가산 하루짜리 이동 포인터 변수인 curr_d의 초기 출발 개시 시점 값을 시작일 객체 start_d 위치로 변경 세팅 지정 설정
        while curr_d <= end_d:  # 이동 포인터 날짜 변수 curr_d의 시점 위치가 최종 마감 통제선인 종료일 end_d 객체 시점 위치보다 <= 작거나 완전히 같을 때까지만 딱 도달하도록 내부 집계 하루 가산 루틴 살림을 루프 반복 가동 실행
            ds = date_to_str(curr_d)  # 현재 포인터가 가리키며 머무르고 있는 특정 하루 날짜 객체 curr_d를 집계 사전 딕셔너리 고유 텍스트 검색 키로 등록 사용하기 위해 외부 범용 호환 표준 규격인 YYYY-MM-DD 문자열 포맷 구조로 변환 가공해 변수 ds에 저장
            date_counts[ds] = date_counts.get(ds, 0) + 1  # 집계 사전 date_counts 주머니 안에서 현재 날짜 글자 ds 키를 찾아 기존 누적 밸류 값을 퍼오되, 만약 아예 첫 등록인 무 텅 빈 상태라 못 찾으면 안전 기본 디폴트 0 수치 값으로 셋팅 대체하여 뽑아온 뒤, 이 하루짜리 블록 가치를 1만큼 추가 가산 더해 다시 딕셔너리에 덮어써서 당일 스케줄 밀집도 카운트 값을 증가 최신화 기록 업데이트
            curr_d = curr_d + datetime.timedelta(days=1)  # 오늘 하루치 집계 밀집도 누적 장부 작성 임무가 완수되었으므로 포인터 날짜 객체 curr_d 공간에 정확히 1일(하루)을 더해 내일 새 날짜 객체로 전진 이동시켜 덮어씀 최신화

    sorted_dates = sorted(date_counts.keys())  # 모든 일정 데이터의 집계 장부 기록 쪼개기 루틴이 싹 완료된 후, 차트 막대그래프 가로축 X라인 상에 시간 흐름의 직관적 가독 순서대로 나열 표기하기 위해 집계 딕셔너리에 수립 기록된 날짜 고유 키 문자열 리스트 목록 전체를 뽑아내 오름차순 시간 정렬하여 변수 sorted_dates 상자에 이관 저장
    chart_counts = [date_counts[d] for d in sorted_dates]  # 정렬 보장 완성된 가로축 날짜 문자열 목록 sorted_dates에서 날짜 키 d를 하나씩 뽑으며, 가로축 진행 순번 정렬 싱크 좌표와 완벽히 1:1 대조 매칭 대응되도록 집계 사전에서 뽑아낸 최종 밀집도 카운트 밸류 수치 값들만을 순서대로 모아 단일 y축 값 리스트 컴프리헨션 생성 조립을 통해 변수 chart_counts 배열에 대입 수집 추가 가산 저장

    plt.close("all")  # 기존에 사용자 호출로 먼저 여러 겹 열려있어 겹쳐서 누적 쌓여있을지도 모르는 모든 과거 잉여 파이플롯 차트 창 캔버스 객체들을 전부 한 번에 싹 다 닫아 깨끗이 소거해버림으로써 메모리 누수 그래프창 겹침 누적 꼬임 렌더링 충돌 오류 현상을 사전 안전 원천 차단 방지 방어
    plt.figure(figsize=(10, 5))  # 파이플롯 라이브러리 plt.figure 도구 함수를 연동 사용 구동해 차트 뷰포트 가로 비율 크기는 10, 세로 비율 크기는 5 수치 사이즈 넓은 규격으로 탁 트인 이쁘고 시원한 새 단일 시각화 데이터 통합 막대 차트 그래프 스케치북 전용 도화지 팝업 창 레이어를 신규 생성 개설 마련
    plt.bar(sorted_dates, chart_counts)  # 가로 x축 속성에 정렬 날짜 리스트 sorted_dates를 붓고, 세로 y축 기둥 길이 속성에 매칭 빈도수 리스트 chart_counts를 부어넣어 날짜별 하루 일정 개수 등락 직관 확인용 세로형 수직 막대그래프 바를 메인 도화지에 빌딩 생성 드로잉 렌더링
    plt.title("Daily Schedule Count")  # 차트 스케치북 레이어 맨 최상단 헤더 구역 공간에 그래프의 정체와 대주제를 한눈에 명시해 주는 대장 제목 메인 타이틀 글자를 "Daily Schedule Count" (일별 일정 카운트) 영문 텍스트 문구 지정으로 각인 셋팅 설정
    plt.xlabel("Date")  # 차트 하단 가로 X축 방향의 속성 의미를 해석 가이드 명시해 주기 위해 가로축 명칭 네임택 라벨 글자를 "Date" (날짜) 영문 텍스트 문구 지정으로 안착 각인 셋팅 설정
    plt.ylabel("Count")  # 차트 측면 세로 Y축 방향의 속성 의미를 해석 가이드 명시해 주기 위해 세로축 명칭 네임택 라벨 글자를 "Count" (개수) 영문 텍스트 문구 지정으로 안착 각인 셋팅 설정
    plt.xticks(rotation=45)  # 하단 X축 구역에 빽빽하게 빼곡히 나열 각인될 YYYY-MM-DD 긴 형식의 가로축 날짜 명칭 텍스트 글자들이 서로 양옆으로 겹치고 먹히며 뭉개지는 폰트 깨짐 겹침 충돌 현상을 막기 위해 글자 축의 각도 속성을 기울기 45도 사선 회전 꺾임 형태로 미려하게 비틀어 표시 노출 자동 변경 조절 최적화 회전 조치
    plt.tight_layout()  # 그래프 메인 타이틀, X/Y축 명칭 라벨 이름표, 사선 날짜 글자들이 비좁은 여백 부족 문제로 화면 바깥 외곽으로 잘려나가 절단 증발 이탈하는 현상 발생을 전면 차단하기 위해 캔버스 전체 컴포넌트 여백 레이아웃을 컴퓨터가 스마트하게 알아서 자동 최적 조절해 이쁘게 꽉 맞춰 핏 조여주는 셋팅 자동 조화 정렬 적용
    plt.show()  # 내부 백그라운드 메모리에서 모든 캔버스 부품 결합 빌딩 조합 조립 및 렌더링 스케치 연산 드로잉 처리가 100% 완벽히 끝난 완성형 단일 통합 시각 차트 히스토그램 막대그래프 스케치북 도화지 창 레이어를 사용자 모니터 화면 뷰포트에 팝업창으로 짜잔 하고 실제 최종 출력 팝업 노출 띄움


root = tk.Tk()  # 모든 위젯 컴포넌트들의 토대 대장 기반이 되는 메인 프로그램 베이스 루트 GUI 화면 윈도우 스케줄러 창 레이어 객체를 최초 생성하여 변수 root에 지정 저장
root.title("일정 관리 시스템 (기간 연속일정)")  # 메인 root 윈도우 창 제목을 기간 연속일정 버전에 맞게 설정
root.geometry("760x600")  # 기간 달력 버튼과 재배치된 버튼 구성을 고려해 메인 창 크기를 가로 760, 세로 600으로 설정
root.resizable(False, False)  # 사용자가 마우스 드래그를 통해 프로그램 메인 윈도우 창 모서리를 임의로 붙잡고 당기거나 비틀어 고정된 최적 설계 UI 레이아웃 화면 폼 크기를 찌그러뜨릴 수 없도록 가변 축소 확장 변경 불가능하게 강제 고정 락 잠금 설정

title_label = tk.Label(root, text="일정 관리 시스템", font=("Arial", 18, "bold"))  # 메인 창 내부 상판 최상단에 앱 정체성을 노출해줄 굵고 커다란 18 크기의 타이틀 대장 제목 라벨 위젯을 텍스트 속성 주어 생성해 변수 title_label에 저장
title_label.pack(pady=10)  # 생성 완수된 메인 윈도우 대장 제목 타이틀 라벨 컴포넌트를 위아래 바깥 세로 여백 10 비율 수치 규격을 넉넉하게 지정 부여하여 상단 구역 한가운데에 이쁘게 정식 안착 패킹 정렬 배치

input_frame = tk.Frame(root)  # 할일 명칭, 약속 시작 및 종료 날짜, 중요도 우선순위, 서브메모 등 각종 데이터 기재 입력창 칸 위젯 부품들과 안내 이름표 컴포넌트들을 단정하게 표 형태로 정렬 수용 보관해줄 입력 전용 껍데기 빈 프레임 상자를 생성하여 변수 input_frame에 할당 저장
input_frame.pack(pady=5)  # 위젯 항목 정렬 전용 껍데기 프레임 상자인 input_frame 위젯의 상하 외부 레이아웃 바깥 여백 정렬 패킹 비율을 5 수치로 알맞게 지정 설정해 메인 창 상판 위에 정식 안착 배치

tk.Label(input_frame, text="할 일").grid(row=0, column=0, padx=5, pady=5)  # 어떤 텍스트를 기재할지 가이드 명시하는 할일 전용 이름표 안내 라벨 컴포넌트를 격자 레이아웃 구조의 가장 첫 단락인 0행 0열 자리 위치에 안착 등록 배치
entry_task = tk.Entry(input_frame, width=25)  # 실제 일정의 핵심 타이틀 제목인 신규 할 일 글자 텍스트를 유저로부터 키보드 타이핑 기재 입력받을 글자 입력창 본체 위젯을 너비 25 수치 규격 크기로 생성하여 변수 entry_task에 할당 저장
entry_task.grid(row=0, column=1, padx=5, pady=5)  # 할일 글자 타이핑 텍스트 입력창 컴포넌트 위젯을 가이드 이름표 바로 옆 칸인 입력 프레임 격자의 0행 1열 위치 자리에 안착 등록 배치

tk.Label(input_frame, text="시작 날짜(YYYY-MM-DD)").grid(row=0, column=2, padx=5, pady=5)  # 스케줄 개시 시작 날짜 기재 구역임을 가이드 명시하는 이름표 안내 라벨 위젯을 입력 프레임 격자 레이아웃 구조의 0행 2열 자리 위치에 안착 등록 배치
entry_start = tk.Entry(input_frame, width=15)  # 스케줄 개시 시작 날짜 글자 텍스트 문자열을 유저로부터 수동 타이핑 기재 입력받을 텍스트 입력창 본체 위젯을 너비 15 수치 규격 크기로 콤팩트하게 생성하여 변수 entry_start에 할당 저장
entry_start.grid(row=0, column=3, padx=5, pady=5)  # 시작 날짜 타이핑 텍스트 글자 입력창 컴포넌트 위젯을 가이드 이름표 바로 옆 칸인 입력 프레임 격자의 0행 3열 위치 자리에 안착 등록 배치
entry_start.insert(0, str(datetime.date.today()))  # 타이핑 수고를 덜어주는 편의 조치로서 앱 로드 즉시 메인 시작 날짜 텍스트 입력창 칸 내부 알맹이에 실시간 현재 컴퓨터 기준의 오늘 날짜 YYYY-MM-DD 문자열 조각 내용을 선제 디폴트 주입 채움

tk.Button(
    input_frame,
    text="기간 달력",
    width=10,
    command=lambda: open_range_calendar(root, set_main_dates)
).grid(row=0, column=4, rowspan=2, padx=8, pady=5, sticky="ns")  # 시작일과 종료일을 팝업 달력에서 두 번 클릭으로 선택할 수 있게 하는 기간 달력 버튼을 입력창 오른쪽에 배치

tk.Label(input_frame, text="우선순위").grid(row=1, column=0, padx=5, pady=5)  # 스케줄 중요도 우선순위 선택 구역임을 가이드 명시하는 이름표 안내 라벨 위젯을 입력 프레임 격자 레이아웃 구조의 1행 0열 자리 위치에 안착 등록 배치
priority_var = tk.StringVar(value="보통")  # 드롭다운 메뉴 콤보 박스 장치의 단계 항목 선택 동작을 내부 백그라운드 메모리에서 실시간 지탱 연동 제어할 tkinter 문자 변수를 생성하고 디폴트 기본 선택 시작값을 "보통" 명칭 상태로 지정 설정
priority_menu = tk.OptionMenu(input_frame, priority_var, "긴급", "높음", "보통", "낮음")  # 사용자가 마우스 클릭으로 4단계 허용 규격("긴급", "높음", "보통", "낮음") 항목들 중 택 1 지정할 수 있도록 지원하는 드롭다운 옵션 메뉴 컴포넌트 장치를 격자판 위에 연동 셋팅 생성
priority_menu.config(width=20)  # 드롭다운 선택 버튼 표면 위젯 껍데기의 좌우 글자 노출 디자인 너비 가로 폭 한계 크기를 여유롭게 20 규격 수치 크기로 변경 옵션 조절 지정 설정
priority_menu.grid(row=1, column=1, padx=5, pady=5)  # 중요도 단계 선택 드롭다운 옵션 메뉴 컴포넌트 위젯을 가이드 이름표 바로 옆 칸인 입력 프레임 격자의 1행 1열 위치 자리에 안착 등록 배치

tk.Label(input_frame, text="종료 날짜(YYYY-MM-DD)").grid(row=1, column=2, padx=5, pady=5)  # 스케줄 통제 마감 종료 날짜 기재 구역임을 가이드 명시하는 이름표 안내 라벨 위젯을 입력 프레임 격자 레이아웃 구조의 1행 2열 자리 위치에 안착 등록 배치
entry_end = tk.Entry(input_frame, width=15)  # 스케줄 통제 마감 종료 날짜 글자 텍스트 문자열을 유저로부터 수동 타이핑 기재 입력받을 텍스트 입력창 본체 위젯을 너비 15 수치 규격 크기로 콤팩트하게 생성하여 변수 entry_end에 할당 저장
entry_end.grid(row=1, column=3, padx=5, pady=5)  # 종료 날짜 타이핑 텍스트 글자 입력창 컴포넌트 위젯을 가이드 이름표 바로 옆 칸인 입력 프레임 격자의 1행 3열 위치 자리에 안착 등록 배치
entry_end.insert(0, str(datetime.date.today()))  # 타이핑 수고를 덜어주는 편의 조치로서 앱 로드 즉시 메인 종료 날짜 텍스트 입력창 칸 내부 알맹이에 실시간 현재 컴퓨터 기준의 오늘 날짜 YYYY-MM-DD 문자열 조각 내용을 선제 디폴트 주입 채움

tk.Label(input_frame, text="메모").grid(row=2, column=0, padx=5, pady=5)  # 부가 설명 기재 서브 메모 기재 구역임을 가이드 명시하는 이름표 안내 라벨 위젯을 입력 프레임 격자 레이아웃 구조의 2행 0열 자리 위치에 안착 등록 배치
entry_memo = tk.Entry(input_frame, width=50)  # 부가 설명 서브 메모 텍스트 글자 문자열을 유저로부터 넉넉하게 긴 문장으로 타이핑 기재 입력받을 넓은 텍스트 입력창 본체 위젯을 너비 50 규격 대형 크기로 큼직하게 생성하여 변수 entry_memo에 할당 저장
entry_memo.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")  # 대형 메모 텍스트 입력창 위젯 컴포넌트를 가로 3칸 분량의 넓은 열 병합 공간 확장 속성을 부여 주어 격자의 2행 1열 서쪽 좌측 정렬 구역 위치에 시원하게 꽉 채워 안착 밀착 등록 배치

button_frame = tk.Frame(root)  # 앱 조작 조종 핵심 컨트롤러 기능 버튼 단추 컴포넌트 위젯 묶음들을 하나의 폼 덩어리로 단정하게 정렬 가두어 수용 보관해 줄 하단 빈 제어 프레임 상자를 별도로 생성하여 변수 button_frame에 할당 저장
button_frame.pack(pady=8)  # 조작 컨트롤 버튼 정렬용 대형 프레임 껍데기 상자인 button_frame 위젯의 상하 외부 바깥 여백 8 비율을 지정 부여해 본체 상판 위에 최종 정식 패킹 정렬 배치

# 버튼 배치는 사용 흐름에 맞춰 3열 구조로 정리합니다.
# 1열: 등록과 전체 확인 기능인 일정 추가, 전체 보기
# 2열: 날짜 관련 기능인 D-day 조회, 날짜별 조회, 날짜별 시각화, CSV 저장
# 3열: 정렬과 관리 기능인 우선순위 정렬, 선택 수정, 선택 삭제, 전체 초기화
btn_specs = [
    ("일정 추가", add_schedule, 0, 0),
    ("전체 보기", show_all, 0, 1),
    ("D-day 조회", open_dday_window, 1, 0),
    ("날짜별 조회", open_date_search_window, 1, 1),
    ("날짜별 시각화", show_date_chart, 1, 2),
    ("CSV 저장", export_to_csv, 1, 3),
    ("우선순위 정렬", sort_by_priority, 2, 0),
    ("선택 수정", edit_selected, 2, 1),
    ("선택 삭제", delete_selected, 2, 2),
    ("전체 초기화", reset_all_schedules, 2, 3),
]  # 버튼 이름, 연결 함수, 행 번호, 열 번호를 한 묶음으로 관리하는 버튼 명세 리스트

for text, cmd, r, c in btn_specs:  # 버튼 명세 리스트에서 버튼 이름과 연결 함수 및 배치 좌표를 하나씩 꺼내 반복
    tk.Button(button_frame, text=text, width=16, command=cmd).grid(row=r, column=c, padx=4, pady=4)  # 좌표 row=r, column=c 규칙에 맞춰 버튼 위젯을 검정 글씨 기본 상태로 일괄 정렬 배치

status_label = tk.Label(root, text="", font=("Arial", 10))  # 메인 창 레이어 허리 구역 정중앙 위치에 전체 일정 개수, 오늘 일정 개수, 오늘 날짜 요약 등 시스템 종합 통계 현황 정보를 보여줄 실시간 상태 라벨 문자 컴포넌트를 생성해 변수 status_label에 저장
status_label.pack(pady=5)  # 종합 상황판 현황 문자 라벨 status_label 컴포넌트를 상하 바깥 세로 여백 5 비율 수치를 넉넉하게 지정 부여해 메인 화면 상판 한가운데에 이쁘게 안착 패킹 정렬 배치

result_frame = tk.Frame(root)  # 앱 조작의 최종 출력물인 결과 줄글 창 리스트박스와 세로 조작 스크롤 막대 바 위젯들을 가로 일렬 이쁘게 정렬 가두어줄 메인 결과 뷰포트 전용 하단 바구니 프레임을 생성하여 변수 result_frame에 할당 저장
result_frame.pack(pady=5)  # 결과 뷰포트 전용 바구니 프레임 result_frame 상자를 위아래 바깥 세로 여백 5 공식 수치 비율을 지정 부여 적용해 메인 화면 맨 아래 하단 구역에 정식 패킹 정렬 배치

scrollbar = tk.Scrollbar(result_frame)  # 하단 결과창 리스트박스 내부 아이템 개수 폭발 팽창 시 긴 목록 리스트 조작을 매끄럽게 서포트해줄 전용 세로 스크롤바 막대 컴포넌트를 생성하여 변수 scrollbar에 할당 저장
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # 세로 스크롤 조작 막대 컴포넌트를 바구니 프레임 구역 내의 가장 우측 끝자락 동쪽 구역에 부착하고 세로축 Y 높이 방향으로 쭉 꽉 채워 팩 정렬 안착 배치

result_box = tk.Listbox(result_frame, width=105, height=15, yscrollcommand=scrollbar.set)  # 각종 조회 및 가상 전개 결과 일정표 항목 문장 줄글들을 유저 화면에 실시간 연속 표출해줄 거대 메인 결과 리스트박스 컴포넌트를 넉넉한 15 줄 규격으로 생성하여 변수 result_box에 지정 저장
result_box.pack(side=tk.LEFT)  # 메인 결과 표출 리스트박스 result_box 본체 위젯을 바구니 프레임 공간 내부의 가장 왼쪽 서쪽 위치 구역 자리에 꽉 들어차게 정렬 안착 팩 배치

scrollbar.config(command=result_box.yview)  # 세로 스크롤 조작 막대를 마우스로 붙잡아 드래그 연산 상하 스킵 이동 시 세로축 상호작용 링크가 긴밀 연동되어 메인 리스트박스 내부의 화면 가상 뷰포트도 함께 이동하도록 세팅 셋팅 연결 맵핑

load_schedules()  # 앱 구동 GUI 뼈대 컴포넌트 세팅 조립이 모두 완수된 최초 시동 시점에 과거 보존된 schedules.txt 하드디스크 텍스트 파일 데이터베이스로부터 전체 일정 기록 정보 내역들을 메인 메모리로 싹 다 로드해 불러오는 내부 연동 함수를 최우선 선제 1회 가동 실행
show_all()  # 하드디스크 저장소 파일로부터 메모리에 성공 로드 장착 완료된 전체 저장 일정 리스트 목록 정보 텍스트 현황을 메인 결과창 리스트박스 뷰포트 화면에 최신 전체 보기 압축 모드로 표출 출력해 주는 연동 함수를 즉시 1회 자동 실행

root.mainloop()  # 메인 프로그램 GUI 윈도우 스케줄러 창 레이어 토대 객체가 시스템 상에서 임의로 꺼져 파괴되지 않고 유저의 모든 마우스 클릭 키보드 타이핑 등 각종 이벤트 입력을 영구 무한 연속 대기 모니터링하며 대기 루프 구동되도록 Tkinter 전용 무한 루프 이벤트 심장 엔진을 정식 가동 작동 셋업 설정