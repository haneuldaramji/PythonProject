import tkinter as tk #tkinter을 tk 이름으로 호출
import tkinter.messagebox as messagebox #tkinter의 messagebox모듈을 messagebox 이름으로 호출
import datetime #날짜계산 위한 datetime 모듈 호출
import calendar #달력 표시용 calendar 모듈 호출
import matplotlib.pyplot as plt #matplotlib의 pyplot모듈을 plt 이름으로 호출

file_name = "schedules.txt" #일정이 저장될 파일이름
schedules = [] #전체일정이 저장될 빈 리스트
current_rows = [] #현재 화면에 보이는 일정들을 저장할 빈 리스트
current_row_meta = [] #현재 화면 일정의 출처(일반/반복 인스턴스) 정보
REPEAT_TYPES = ("daily", "weekly")
REPEAT_LABEL_TO_CODE = {"매일": "daily", "매주": "weekly"}
REPEAT_CODE_TO_LABEL = {"daily": "매일", "weekly": "매주"}
DISPLAY_HORIZON_DAYS = 365 #반복 종료일 미지정 시 화면에 펼칠 기간

    
def is_valid_date(text):  #입력창에 입력된 문자가 올바른 날짜형식인지 검사하는 함수
    parts = text.split("-") #입력창에 입력된 문자를 - 기준으로 나눔.

    if len(parts) != 3: #만약 나누어진 파트의 개수가 세개(연,월,일)가 아니라면
        return False #거짓으로 반환
    
    y = parts[0]  #첫번째파트를 연도y로 지정
    m = parts[1]  #두번째파트를 월m으로 지정
    d = parts[2]  #세번째파트를 일d로 지정
    
    if len(y) != 4 or len(m) != 2 or len(d) != 2:  #만약 연도y가 네자리수, 월m이 두자리수, 일d가 2자리수가 아니라면
        return False #거짓으로 반환

    if not (y.isdigit() and m.isdigit() and d.isdigit()): #만약 연도y,월m,일d가 모두 숫자가 아니라면
        return False #거짓으로 반환
    
    y = int(y) #위 세 조건을 모두 만족하는 문자열 연도y를 정수로 변환
    m = int(m) #위 세 조건을 모두 만족하는 문자열 월m을 정수로 변환
    d = int(d) #위 세 조건을 모두 만족하는 문자열 일d를 정수로 변환

    if y < 1 or y > 9999: #만약 연도y가 datetime.date에서 사용할 수 있는 1~9999 범위 밖이면
        return False #거짓으로 반환

    if m < 1 or m > 12: #만약 월m이 1~12 범위 밖이면
        return False #거짓으로 반환
    
    last_days_of_m = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] #각 월의 마지막 날짜를 리스트로 설정

    if y % 400 == 0 or (y % 4 == 0 and y % 100 != 0):  #만약 연도y가 윤년(4년주기로 2월말일이 29일인해)이면
        last_days_of_m[1] = 29  #2월의 마지막 날짜를 29일로 바꿈   

    if d < 1 or d > last_days_of_m[m - 1]:  #만약 일d가 해당 월의 범위 안에 없으면
        return False #거짓으로 반환
    
    return True  # 위 7가지 if조건에 모두 해당하지 않는 날짜는 참으로 반환


def parse_date_str(text): #YYYY-MM-DD 문자열을 date 객체로 변환
    parts = text.split("-")
    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))


def date_to_str(d): #date 객체를 YYYY-MM-DD 문자열로 변환
    return d.strftime("%Y-%m-%d")


def is_recurring_schedule(s): #반복 일정 마스터인지 확인
    return len(s) >= 6 and s[4] in REPEAT_TYPES


def repeat_label(repeat_type): #반복 주기 표시용 한글 문구
    labels = {"daily": "매일", "weekly": "매주(7일)"}
    return labels.get(repeat_type, repeat_type)


def parse_exceptions(text): #제외된 반복 날짜 집합
    if text == "":
        return set()
    return set(x.strip() for x in text.split(",") if is_valid_date(x.strip()))


def format_exceptions(exc_set): #제외 날짜 집합을 저장 문자열로 변환
    return ",".join(sorted(exc_set))


def parse_overrides(text): #특정 날짜만 수정한 내용 {날짜: [할일, 우선순위, 메모]}
    result = {}
    if text == "":
        return result
    for part in text.split(";"):
        if part == "":
            continue
        pieces = part.split("^")
        if len(pieces) == 4 and is_valid_date(pieces[0]):
            result[pieces[0]] = [pieces[1], pieces[2], pieces[3]]
    return result


def format_overrides(override_dict): #override_dict를 저장 문자열로 변환
    parts = []
    for date in sorted(override_dict.keys()):
        task, priority, memo = override_dict[date]
        parts.append(date + "^" + task + "^" + priority + "^" + memo)
    return ";".join(parts)


def open_calendar_picker(parent, on_select, current_date="", min_date=""): #달력에서 날짜 선택
    win = tk.Toplevel(parent)
    win.title("반복 종료일 선택")
    win.resizable(False, False)
    win.grab_set()

    if current_date != "" and is_valid_date(current_date):
        view = parse_date_str(current_date)
    else:
        view = datetime.date.today()

    state = {"year": view.year, "month": view.month}
    body = tk.Frame(win)
    body.pack(padx=12, pady=10)

    nav = tk.Frame(body)
    nav.pack(pady=(0, 6))
    title_label = tk.Label(nav, text="", font=("Arial", 12, "bold"))
    title_label.pack(side=tk.LEFT, padx=10)

    grid_frame = tk.Frame(body)
    grid_frame.pack()

    def change_month(delta):
        y = state["year"]
        m = state["month"] + delta
        if m < 1:
            m = 12
            y -= 1
        elif m > 12:
            m = 1
            y += 1
        state["year"] = y
        state["month"] = m
        render_days()

    tk.Button(nav, text="<", width=3, command=lambda: change_month(-1)).pack(side=tk.LEFT)
    tk.Button(nav, text=">", width=3, command=lambda: change_month(1)).pack(side=tk.RIGHT)

    def pick_date(day):
        picked = datetime.date(state["year"], state["month"], day)
        picked_str = date_to_str(picked)
        if min_date != "" and is_valid_date(min_date) and picked_str < min_date:
            messagebox.showerror("선택 오류", "반복 종료일은 일정 시작일보다 빠를 수 없습니다.", parent=win)
            return
        on_select(picked_str)
        win.destroy()

    def render_days():
        for child in grid_frame.winfo_children():
            child.destroy()

        y = state["year"]
        m = state["month"]
        title_label.config(text=str(y) + "년 " + str(m) + "월")

        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for col, name in enumerate(weekdays):
            tk.Label(grid_frame, text=name, width=4).grid(row=0, column=col, pady=2)

        month_days = calendar.monthcalendar(y, m)
        today = datetime.date.today()
        selected = current_date if is_valid_date(current_date) else ""

        for row_index, week in enumerate(month_days, start=1):
            for col_index, day in enumerate(week):
                if day == 0:
                    tk.Label(grid_frame, text="", width=4).grid(row=row_index, column=col_index)
                    continue

                day_str = date_to_str(datetime.date(y, m, day))
                btn_text = str(day)
                if day_str == date_to_str(today):
                    btn_text = str(day) + "*"

                state_btn = tk.NORMAL
                if min_date != "" and is_valid_date(min_date) and day_str < min_date:
                    state_btn = tk.DISABLED

                btn = tk.Button(grid_frame, text=btn_text, width=4, state=state_btn,
                                command=lambda d=day: pick_date(d))
                if day_str == selected:
                    btn.config(relief=tk.SUNKEN)
                btn.grid(row=row_index, column=col_index, padx=1, pady=1)

    render_days()

    tk.Label(body, text="* 오늘 날짜", font=("Arial", 9)).pack(pady=(6, 4))
    tk.Button(body, text="종료일 없음", width=14,
              command=lambda: (on_select(""), win.destroy())).pack(pady=2)


def make_date_picker(parent, date_var, min_date_getter=None): #날짜 표시 + 달력/지우기 버튼 묶음
    frame = tk.Frame(parent)
    display = tk.Label(frame, text="선택 안 함", width=14, anchor="w")

    def refresh_display(*_):
        value = date_var.get().strip()
        if value == "":
            display.config(text="선택 안 함")
        else:
            display.config(text=value)

    def open_picker():
        min_date = ""
        if min_date_getter is not None:
            min_date = min_date_getter().strip()
            if min_date != "" and not is_valid_date(min_date):
                min_date = str(datetime.date.today())
        open_calendar_picker(parent, date_var.set, date_var.get().strip(), min_date)

    display.pack(side=tk.LEFT)
    tk.Button(frame, text="달력", width=6, command=open_picker).pack(side=tk.LEFT, padx=3)
    tk.Button(frame, text="지우기", width=6, command=lambda: date_var.set("")).pack(side=tk.LEFT)
    date_var.trace_add("write", refresh_display)
    refresh_display()
    return frame


def get_series_end(master): #반복 일정의 마지막 발생일
    if len(master) > 5 and master[5] != "" and is_valid_date(master[5]):
        return parse_date_str(master[5])
    start = parse_date_str(master[1])
    return start + datetime.timedelta(days=DISPLAY_HORIZON_DAYS)


def iter_occurrence_dates(master): #반복 마스터의 발생 날짜를 순서대로 생성
    current = parse_date_str(master[1])
    end = get_series_end(master)
    repeat = master[4]
    while current <= end:
        yield current
        if repeat == "weekly":
            current += datetime.timedelta(days=7)
        else:
            current += datetime.timedelta(days=1)


def resolve_instance(master, occ_date): #특정 날짜의 실제 표시 일정(override 반영)
    overrides = parse_overrides(master[7] if len(master) > 7 else "")
    if occ_date in overrides:
        task, priority, memo = overrides[occ_date]
        return [task, occ_date, priority, memo]
    return [master[0], occ_date, master[2], master[3]]


def expand_schedules_for_display(source_schedules): #저장 일정을 화면용 일정+메타로 펼침
    rows = []
    meta = []
    for s in source_schedules:
        if is_recurring_schedule(s):
            exceptions = parse_exceptions(s[6] if len(s) > 6 else "")
            for d in iter_occurrence_dates(s):
                ds = date_to_str(d)
                if ds in exceptions:
                    continue
                rows.append(resolve_instance(s, ds))
                meta.append({"kind": "instance", "master": s, "date": ds})
        else:
            rows.append(s[:4])
            meta.append({"kind": "normal", "schedule": s})
    return rows, meta


def sort_rows_with_meta(rows, meta, key_func): #일정과 메타를 같이 정렬
    paired = list(zip(rows, meta))
    paired.sort(key=lambda x: key_func(x[0]))
    if len(paired) == 0:
        return [], []
    sorted_rows, sorted_meta = zip(*paired)
    return list(sorted_rows), list(sorted_meta)


def make_dday_text(target_date): #D-day 목표일 target_date까지의 D-day날짜 문자를 만드는 함수
    parts = target_date.split("-")  #목표일을 - 기준으로 나눔
    target = datetime.date(int(parts[0]), int(parts[1]), int(parts[2])) #목표일 문자열을 정수로 바꾼 후 날짜객체로 변환
    diff = (target - datetime.date.today()).days #diff=목표일의날짜객체-현재시점오늘날짜

    if diff > 0: #만약 diff가 >0 이면
        return "D-" + str(diff) #D-diff일자를 반환
    elif diff == 0: #만약 diff가 =0 이면
        return "D-Day" #D-Day를 반환
    else: #diff가 <0 이면
        return "D+" + str(abs(diff)) #D+절대값(diff)일자를 반환
    

def load_schedules(): #지정한 파일에서 전체일정을 불러오는 함수
    schedules.clear() #기존 전체일정 리스트를 비움
    open(file_name, "a", encoding="utf-8").close()  #파일이 없으면 새로 만들고 바로 닫음.

    with open(file_name, "r", encoding="utf-8") as f:  #파일을 읽기모드로 엶
        for line in f:  #파일내용을 한줄씩 반복해서 읽음
            data = line.strip().split("|")  #한 줄씩 읽은 문장의 양쪽공백을 제거하고 | 기준으로 나눠 리스트 data로 전환

            if len(data) == 4:  #만약 리스트data의 요소 갯수가 4개면
                task = data[0]  #첫 요소는 task(할일)로 지정
                date = data[1]   #두번째는 date(날짜)로 지정
                priority = data[2] #세번째는 priority(우선순위)로 지정
                memo = data[3]  #네번째는 memo(메모)로 지정

                if is_valid_date(date) and priority in ["긴급", "높음", "보통", "낮음"]: #날짜가 올바르고 우선순위가 4단계 중 하나이면
                    schedules.append([task, date, priority, memo]) #schedules 리스트에 [task, date, priority, memo] 형태로 추가

            elif len(data) >= 6: #반복 일정(6필드 이상)
                task = data[0]
                date = data[1]
                priority = data[2]
                memo = data[3]
                repeat = data[4]
                end_date = data[5] if len(data) > 5 else ""
                exceptions = data[6] if len(data) > 6 else ""
                overrides = data[7] if len(data) > 7 else ""

                if is_valid_date(date) and priority in ["긴급", "높음", "보통", "낮음"] and repeat in REPEAT_TYPES:
                    if end_date != "" and not is_valid_date(end_date):
                        end_date = ""
                    schedules.append([task, date, priority, memo, repeat, end_date, exceptions, overrides])

def save_schedules():  #전체일정을 요소 사이에 |를 추가해서 파일에 저장하는 함수
    with open(file_name, "w", encoding="utf-8") as f: #파일을 쓰기모드로 엶
        for s in schedules: #전체일정리스트(schedules리스트)에서 일정을 하나씩 꺼냄
            if len(s) == 4:
                f.write(s[0] + "|" + s[1] + "|" + s[2] + "|" + s[3] + "\n")
            else:
                while len(s) < 8:
                    s.append("")
                f.write(s[0] + "|" + s[1] + "|" + s[2] + "|" + s[3] + "|" + s[4] + "|" + s[5] + "|" + s[6] + "|" + s[7] + "\n")


def clear_input_fields(): #입력창(할일,날짜, 우선순위, 메모 옆에 텍스트를 입력하는 칸)을 새로고침하는 함수
    entry_task.delete(0, tk.END) #할일입력창 빈칸으로 새로고침
    entry_date.delete(0, tk.END) #날짜입력창 빈칸으로 새로고침
    priority_var.set("보통") #우선순위를 기본값 보통으로 초기화
    entry_memo.delete(0, tk.END) #메모입력창 빈칸으로 새로고침

    entry_date.insert(0, str(datetime.date.today())) #삭제된 날짜입력창에 현재시점 오늘 날짜 다시 입력


def update_status():  #가운데 위치한 상태표시문장(ex 총 일정: 4개 | 오늘 일정: 0개 | 오늘 날짜: 2026-05-17) 한줄을 매 입력마다 새로고침하는 함수
    today = str(datetime.date.today()) #현재시점 오늘날짜를 YYYY-MM-DD형식 문자열로 저장
    today_count = 0 #오늘일정개수담는 변수

    rows, _ = expand_schedules_for_display(schedules)
    for s in rows:
        if s[1] == today:
            today_count += 1

    text = f"총 일정: {len(rows)}개 | 오늘 일정: {today_count}개 | 오늘 날짜: {today}" #화면에 표시되는 문장

    status_label['text'] = text #상태표시라벨의 기존글자를 위에서 만든 text로 최신화


def show_rows(rows, empty_msg, dday_mode, rows_meta=None):  #rows 리스트 속 일정들을 결과창에 표시하는 함수
    current_rows.clear()  #현재 화면에 표시된 실제 일정 데이터 목록을 비움
    current_row_meta.clear()
    result_box.delete(0, tk.END) #결과창(Listbox)에 보이는 기존 문장들을 모두 삭제

    if len(rows) == 0:  #만약 rows 리스트 속 일정이 0개면
        result_box.insert(tk.END, empty_msg)  #전체일정표시창에 "등록된 일정이 없습니다" 안내문구 띄움
    else: #rows 리스트 속 일정이 0개가 아니면
        num = 1 #일정번호를 1부터 시작하도록 지정

        for i, s in enumerate(rows): #rows 리스트 속 일정을 하나씩 꺼내서 반복
            current_rows.append(s) #current_row 리스트에 rows리스트에서 꺼낸 일정을 하나씩 추가
            if rows_meta is not None and i < len(rows_meta):
                current_row_meta.append(rows_meta[i])
            else:
                current_row_meta.append({"kind": "normal", "schedule": s})

            task = s[0] #일정의 첫번째요소를 할일(task)로 지정
            date = s[1] #일정의 두번째요소를 날짜(date)로 지정
            priority = s[2] #일정의 세번째요소를 우선순위(priority)로 지정
            memo = s[3] #일정의 네번째요소를 메모(memo)로 지정

            dday = "" #디데이 문구를 담을 dday변수를 빈 문자열로 초기화
            if dday_mode: #만약 디데이 출력모드가 켜져있으면
                dday = f"{make_dday_text(date)} | " 

            memo_part = ""
            if memo != "": #만약 메모가 빈 문자열이 아니라면
                memo_part = f" | 메모: {memo}"

            repeat_part = ""
            if current_row_meta[-1]["kind"] == "instance":
                repeat_part = f" | [반복:{repeat_label(current_row_meta[-1]['master'][4])}]"

            text = f"{num}. {date} | {dday}[{priority}] | {task}{memo_part}{repeat_part}"
            result_box.insert(tk.END, text) #전체일정표시창의 마지막줄에 새 문장추가
            num += 1 #다음일정번호 +1증가

    update_status() #update_status함수 사용하여 가운데 위치한 상태표시문장 새로고침


def read_input_schedule(): # 입력창에 입력하는 문자의 오류를 5가지 검사를 거쳐서 감별하는 함수
                            # 먼저 입력되는 할일, 날짜, 우선순위, 메모 문자의 앞뒤 공백 제거 후
                            # 1.할일입력창에 빈칸으로 입력되는지, 2.|가 섞여있는지, 3.is_valid_date함수통해 날짜형식이 아닌지, 
                            # 4.우선순위입력이 숫자가아니거나 1보다작은지, 5.기존에 등록했던 일정과 중복되는지
                            # 이 다섯가지 검사를 통과하는 일정을 새 일정으로 등록.

    task = entry_task.get().strip() #할일칸에 입력한 문자 공백제거
    date = entry_date.get().strip() #날짜칸에 입력한 문자 공백제거
    priority = priority_var.get() #선택된 우선순위 값을 가져옴
    memo = entry_memo.get().strip() #메모칸에 입력한 문자 공백제거

    if task == "": #만약 할일입력창에 빈칸을 입력하면 
        messagebox.showerror("입력오류", "할 일을 입력하세요.") #입력오류알림창띄움
        return None #None 반환

    if "|" in task or "|" in memo:  #만약 할일입력창과 메모입력창에 | 가 입력되면
        messagebox.showerror("입력오류", "할 일과 메모에는 | 문자를 사용할 수 없습니다.") #입력오류창알림띄움
        return None #None 반환

    if not is_valid_date(date): #날짜입력창에 입력한 문자가 is_valid_date함수의 조건을 만족하지 못하면
        messagebox.showerror("입력 오류", "날짜는 YYYY-MM-DD 형식으로 입력하세요. 예: 2026-05-11") #입력오류알림창띄움
        entry_date.delete(0, tk.END) #날짜입력창에 입력한 문자제거
        entry_date.insert(0, str(datetime.date.today())) #다시 현재시점오늘날짜를 날짜입력창 빈칸에 채움
        return None #None 반환
    
    new_schedule = [task, date, priority, memo] # 검사를 통과한 입력값들을 새 일정리스트로 만듦

    if new_schedule in schedules: # 만약 새로 등록하는 일정리스트가 이미 기존의 전체일정리스트 안에 포함되어있다면
        messagebox.showerror("입력 오류", "이미 등록된 일정입니다.") #입력오류알림창띄움
        return None #None 반환

    return new_schedule #위 다섯가지 조건을 모두 통과한 일정은 new_schedule로 반환


def add_schedule(): #추가한 새 일정을 저장시키는 함수
    new_schedule = read_input_schedule() #read_input_schedule함수의 검사를 통과한 new_schedule변수를 업데이트

    if new_schedule == None: #만약 new_schedule 속 일정이 없다면
        return
    
    schedules.append(new_schedule) #전체일정리스트schedules에 새일정new_schedule 추가
    save_schedules() #save_schedules함수통해 변경된 전체일정리스트를 파일에 저장
    clear_input_fields() #clear_input_fields함수 통해 입력창 새로고침
    show_all() #show_all함수 통해 전체일정 출력


def sort_key_by_date_priority(s): #전체일정 정렬시 날짜를 1순위, 우선순위를 2순위로 정렬하는 기준 함수
    priority_order = {"긴급": 1, "높음": 2, "보통": 3, "낮음": 4} #우선순위별 정렬 순서 지정
    date = s[1] #일정의 두번째요소인 날짜 지정
    priority = priority_order[s[2]] #문자 우선순위를 숫자 정렬값으로 변환
    return (date, priority) #날짜와 우선순위를 정렬 세트로 반환


def show_all(): #전체일정리스트를 화면에 출력하는 함수
    rows, meta = expand_schedules_for_display(schedules)
    rows, meta = sort_rows_with_meta(rows, meta, sort_key_by_date_priority)
    show_rows(rows, "등록된 일정이 없습니다.", False, meta) #부합하는 일정들을 결과창에 출력

    
def open_date_input_window(title, guide_text, button_text, dday_mode):  # 날짜별조회 입력용/D-day계산입력용 보조창을 여는 함수
    win = tk.Toplevel(root) # 메인창 위에 새 보조창 만듦
    win.title(title) # 보조창 제목 title로 설정
    win.geometry("360x170") # 보조창 크기 가로360 세로170으로 설정
    win.resizable(False, False) # 보조창 크기변경 불가능하게 설정

    tk.Label(win, text=guide_text, font=("Arial", 11, "bold")).pack(pady=8) # 보조창에 안내문구 라벨을 배치
    tk.Label(win, text="형식: YYYY-MM-DD  예: 2026-05-11").pack() # 보조창에 형식 안내 텍스트 배치

    date_entry = tk.Entry(win, width=22, justify="center") # 날짜별조회 입력용/D-day계산입력용 보조창의 입력창 생성
    date_entry.pack(pady=8) #보조창 위아래 여백8로 설정
    date_entry.insert(0, str(datetime.date.today())) #보조창에 현재시점 오늘날짜 미리 입력

    def run(): # 보조창 버튼을 눌렀을 때 실제로 실행되는 내부함수
        target_date = date_entry.get().strip() #보조창에 입력한 값의 양쪽 공백 제거

        if not is_valid_date(target_date): # 만약 입력한 날짜가 날짜 조건을 만족하지 못하면
            messagebox.showerror("입력 오류", "날짜는 YYYY-MM-DD 형식으로 입력하세요.") #입력오류창 생성
            date_entry.delete(0, tk.END) # 보조창 속 입력값 새로고침
            date_entry.insert(0, str(datetime.date.today())) # 새로고침 후 현재시점 오늘날짜 입력
            return # 오류가 났으므로 여기서 실행 중단
        
        all_rows, all_meta = expand_schedules_for_display(schedules)
        rows = []
        meta = []
        for s, m in zip(all_rows, all_meta):
            if s[1] == target_date:
                rows.append(s)
                meta.append(m)

        rows, meta = sort_rows_with_meta(rows, meta, sort_key_by_date_priority)

        show_rows(rows, "해당 날짜의 일정이 없습니다.", dday_mode, meta) # 부합하는 일정들을 결과창에 출력 (dday_mode에 따라 다르게 표시)

        entry_date.delete(0, tk.END) # 메인창 날짜입력창 내용 전부 삭제
        entry_date.insert(0, str(datetime.date.today())) # 메인창 날짜 입력창에 현재시점 오늘날짜 다시 입력

        win.destroy() # 모든 작업이 끝났으므로 날짜별조회 입력용/D-day계산입력용 보조창 닫기

    tk.Button(win, text=button_text, width=12, command=run).pack(pady=5) # 보조창에 실행 버튼(조회 또는 계산)을 생성하고 run함수와 연결


def open_date_search_window(): #날짜별 조회 버튼을 눌렀을 때 날짜별 조회 보조창을 여는 함수
    open_date_input_window("날짜별 조회", "조회할 날짜를 입력하세요.", "조회", False)


def open_dday_window(): #D-day 계산 버튼을 눌렀을 때 D-day 계산 보조창을 여는 함수
    open_date_input_window("D-day 계산", "D-day를 확인할 날짜를 입력하세요.", "계산", True)


def sort_key_by_priority_date(s): #우선순위 정렬시 우선순위를 1순위, 날짜를 2순위로 정렬하는 기준 함수
    priority_order = {"긴급": 1, "높음": 2, "보통": 3, "낮음": 4} #우선순위별 정렬 순서 지정
    date = s[1] #일정의 두번째요소를 날짜로 지정
    priority = priority_order[s[2]] #문자 우선순위를 숫자 정렬값으로 변환
    return (priority, date) #우선순위와 날짜를 정렬 세트로 반환


def sort_by_priority(): #전체일정리스트를 우선순위순으로 화면에 출력하는 함수
    rows, meta = expand_schedules_for_display(schedules)
    rows, meta = sort_rows_with_meta(rows, meta, sort_key_by_priority_date)
    show_rows(rows, "등록된 일정이 없습니다.", False, meta) #show_rows함수 통해 정렬된 전체일정을 일반출력모드로 결과창에 출력


def delete_selected(): #결과창에서 선택한 일정을 삭제하는 함수
    selected = result_box.curselection() #전체일정표시창에서 사용자가 선택한 항목번호를 가져옴

    if len(selected) == 0: #만약 선택된 항목의 개수가 0개면
        messagebox.showerror("선택 오류", "삭제할 일정을 먼저 선택하세요.") #입력오류메시지창 띄움
        return #삭제작업 중단

    if len(current_rows) == 0: #만약 현재 화면에 보이는 일정리스트가 비어있다면
        messagebox.showerror("삭제 오류", "삭제할 일정이 없습니다.") #입력오류메시지창 띄움
        return #삭제작업 중단

    index = selected[0] #선택된 항목번호 중 첫번째 번호를 index에 저장

    if index >= len(current_rows): #만약 선택한 번호가 현재 화면일정리스트 범위 밖이면
        messagebox.showerror("삭제 오류", "삭제할 일정이 없습니다.") #입력오류메시지창 띄움
        return #삭제작업 중단

    target = current_rows[index]
    meta = current_row_meta[index]

    if meta["kind"] == "normal":
        if target in schedules or meta["schedule"] in schedules:
            schedule_ref = meta["schedule"] if meta["schedule"] in schedules else target
            schedules.remove(schedule_ref)
            save_schedules()
            show_all()
            messagebox.showinfo("삭제 완료", "선택한 일정이 삭제되었습니다.")
        else:
            messagebox.showerror("삭제 오류", "삭제할 일정을 찾지 못했습니다.")
        return

    master = meta["master"]
    if master not in schedules:
        messagebox.showerror("삭제 오류", "삭제할 반복 일정을 찾지 못했습니다.")
        return

    answer = messagebox.askyesnocancel("삭제 범위", "예 = 이 날짜만 삭제\n아니오 = 반복 일정 전체 삭제\n취소 = 중단")
    if answer is None:
        return

    if answer:
        exceptions = parse_exceptions(master[6] if len(master) > 6 else "")
        exceptions.add(meta["date"])
        while len(master) < 7:
            master.append("")
        master[6] = format_exceptions(exceptions)
        save_schedules()
        show_all()
        messagebox.showinfo("삭제 완료", "선택한 날짜의 반복 일정만 삭제되었습니다.")
    else:
        schedules.remove(master)
        save_schedules()
        show_all()
        messagebox.showinfo("삭제 완료", "반복 일정 전체가 삭제되었습니다.")


def read_recurring_schedule(): #반복 일정 등록용 입력 검사
    new_schedule = read_input_schedule()
    if new_schedule is None:
        return None

    repeat = REPEAT_LABEL_TO_CODE.get(repeat_var.get(), "")
    if repeat not in REPEAT_TYPES:
        messagebox.showerror("입력 오류", "반복 단위를 매일 또는 매주(7일) 중에서 선택하세요.")
        return None

    end_date = repeat_end_var.get().strip()
    if end_date != "" and not is_valid_date(end_date):
        messagebox.showerror("입력 오류", "반복 종료일은 YYYY-MM-DD 형식이거나 비워 두세요.")
        return None

    if end_date != "" and end_date < new_schedule[1]:
        messagebox.showerror("입력 오류", "반복 종료일은 시작일보다 빠를 수 없습니다.")
        return None

    return [new_schedule[0], new_schedule[1], new_schedule[2], new_schedule[3], repeat, end_date, "", ""]


def add_recurring_schedule(): #반복 일정 추가
    new_schedule = read_recurring_schedule()
    if new_schedule is None:
        return

    if new_schedule in schedules:
        messagebox.showerror("입력 오류", "이미 등록된 반복 일정입니다.")
        return

    schedules.append(new_schedule)
    save_schedules()
    clear_input_fields()
    repeat_end_var.set("")
    show_all()
    messagebox.showinfo("등록 완료", "반복 일정이 등록되었습니다.")


def apply_instance_override(master, occ_date, task, priority, memo): #특정 날짜만 수정 내용 저장
    overrides = parse_overrides(master[7] if len(master) > 7 else "")
    overrides[occ_date] = [task, priority, memo]
    while len(master) < 8:
        master.append("")
    master[7] = format_overrides(overrides)


def open_edit_window(meta, display_row, edit_scope): #일정 수정 보조창
    win = tk.Toplevel(root)
    win.title("일정 수정")
    win.geometry("420x360")
    win.resizable(False, False)

    if edit_scope == "instance":
        scope_text = "이 날짜만 수정"
    elif edit_scope == "series":
        scope_text = "반복 일정 전체 수정"
    else:
        scope_text = "일정 수정"
    tk.Label(win, text=scope_text, font=("Arial", 11, "bold")).pack(pady=8)

    frame = tk.Frame(win)
    frame.pack(pady=5)

    tk.Label(frame, text="할 일").grid(row=0, column=0, padx=5, pady=5)
    edit_task = tk.Entry(frame, width=28)
    edit_task.grid(row=0, column=1, padx=5, pady=5)
    edit_task.insert(0, display_row[0])

    tk.Label(frame, text="날짜").grid(row=1, column=0, padx=5, pady=5)
    edit_date = tk.Entry(frame, width=28)
    edit_date.grid(row=1, column=1, padx=5, pady=5)
    edit_date.insert(0, display_row[1])
    if edit_scope == "instance":
        edit_date.config(state="disabled")

    tk.Label(frame, text="우선순위").grid(row=2, column=0, padx=5, pady=5)
    edit_priority_var = tk.StringVar(value=display_row[2])
    tk.OptionMenu(frame, edit_priority_var, "긴급", "높음", "보통", "낮음").grid(row=2, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame, text="메모").grid(row=3, column=0, padx=5, pady=5)
    edit_memo = tk.Entry(frame, width=28)
    edit_memo.grid(row=3, column=1, padx=5, pady=5)
    edit_memo.insert(0, display_row[3])

    edit_repeat_var = tk.StringVar(value="매일")
    edit_repeat_end_var = tk.StringVar(value="")
    if edit_scope == "series":
        master = meta["master"]
        tk.Label(frame, text="반복").grid(row=4, column=0, padx=5, pady=5)
        edit_repeat_var.set(REPEAT_CODE_TO_LABEL.get(master[4], "매일"))
        edit_repeat_frame = tk.Frame(frame)
        edit_repeat_frame.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        tk.Radiobutton(edit_repeat_frame, text="매일", variable=edit_repeat_var, value="매일").pack(side=tk.LEFT)
        tk.Radiobutton(edit_repeat_frame, text="매주(7일)", variable=edit_repeat_var, value="매주").pack(side=tk.LEFT, padx=8)
        tk.Label(frame, text="반복 종료").grid(row=5, column=0, padx=5, pady=5)
        if len(master) > 5:
            edit_repeat_end_var.set(master[5])
        make_date_picker(frame, edit_repeat_end_var, lambda: edit_date.get()).grid(row=5, column=1, padx=5, pady=5, sticky="w")

    def save_edit():
        task = edit_task.get().strip()
        date = display_row[1] if edit_scope == "instance" else edit_date.get().strip()
        priority = edit_priority_var.get()
        memo = edit_memo.get().strip()

        if task == "":
            messagebox.showerror("입력 오류", "할 일을 입력하세요.", parent=win)
            return
        if "|" in task or "|" in memo:
            messagebox.showerror("입력 오류", "할 일과 메모에는 | 문자를 사용할 수 없습니다.", parent=win)
            return
        if not is_valid_date(date):
            messagebox.showerror("입력 오류", "날짜는 YYYY-MM-DD 형식으로 입력하세요.", parent=win)
            return
        if priority not in ["긴급", "높음", "보통", "낮음"]:
            messagebox.showerror("입력 오류", "우선순위를 선택하세요.", parent=win)
            return

        if meta["kind"] == "normal":
            old = meta["schedule"]
            new_item = [task, date, priority, memo]
            if new_item != old and new_item in schedules:
                messagebox.showerror("입력 오류", "이미 등록된 일정입니다.", parent=win)
                return
            if old in schedules:
                idx = schedules.index(old)
                schedules[idx] = new_item
        elif edit_scope == "instance":
            master = meta["master"]
            if master not in schedules:
                messagebox.showerror("수정 오류", "반복 일정을 찾지 못했습니다.", parent=win)
                return
            apply_instance_override(master, meta["date"], task, priority, memo)
        else:
            master = meta["master"]
            repeat = REPEAT_LABEL_TO_CODE.get(edit_repeat_var.get(), "")
            end_date = edit_repeat_end_var.get().strip()
            if repeat not in REPEAT_TYPES:
                messagebox.showerror("입력 오류", "반복 단위를 매일 또는 매주(7일) 중에서 선택하세요.", parent=win)
                return
            if end_date != "" and not is_valid_date(end_date):
                messagebox.showerror("입력 오류", "반복 종료일 형식이 올바르지 않습니다.", parent=win)
                return
            if end_date != "" and end_date < date:
                messagebox.showerror("입력 오류", "반복 종료일은 시작일보다 빠를 수 없습니다.", parent=win)
                return
            if master in schedules:
                exceptions = master[6] if len(master) > 6 else ""
                overrides = master[7] if len(master) > 7 else ""
                idx = schedules.index(master)
                schedules[idx] = [task, date, priority, memo, repeat, end_date, exceptions, overrides]

        save_schedules()
        show_all()
        win.destroy()
        messagebox.showinfo("수정 완료", "일정이 수정되었습니다.")

    tk.Button(win, text="저장", width=12, command=save_edit).pack(pady=8)


def edit_selected(): #선택한 일정 수정(일반/반복 전체/반복 특정 날짜)
    selected = result_box.curselection()
    if len(selected) == 0:
        messagebox.showerror("선택 오류", "수정할 일정을 먼저 선택하세요.")
        return
    if len(current_rows) == 0:
        messagebox.showerror("수정 오류", "수정할 일정이 없습니다.")
        return

    index = selected[0]
    if index >= len(current_rows):
        messagebox.showerror("수정 오류", "수정할 일정이 없습니다.")
        return

    display_row = current_rows[index]
    meta = current_row_meta[index]

    if meta["kind"] == "normal":
        open_edit_window(meta, display_row, "normal")
        return

    answer = messagebox.askyesnocancel(
        "수정 범위",
        "예 = 이 날짜만 수정\n아니오 = 반복 일정 전체 수정\n취소 = 중단"
    )
    if answer is None:
        return
    if answer:
        open_edit_window(meta, display_row, "instance")
    else:
        master = meta["master"]
        series_row = [master[0], master[1], master[2], master[3]]
        open_edit_window({"kind": "instance", "master": master}, series_row, "series")


def reset_all_schedules(): #등록된 모든 일정을 초기화하는 함수
    answer = messagebox.askyesno("초기화 확인", "등록된 모든 일정을 삭제하시겠습니까?") #전체일정을 삭제할지 예/아니오 메시지창으로 확인

    if answer == False: #만약 사용자가 아니오를 선택했다면
        return #초기화작업 중단

    schedules.clear() #전체일정리스트schedules 내용전부삭제
    current_rows.clear() #현재 화면에 보이는 일정리스트 내용전부삭제
    current_row_meta.clear()
    save_schedules() #비워진 전체일정리스트 상태를 save_schedules함수통해 파일에 저장
    clear_input_fields() #clear_input_fields함수 통해 입력창 내용 초기화
    show_all() #초기화된 전체일정 화면 다시 출력


def show_date_chart(): #날짜별 일정개수를 막대그래프로 시각화하는 함수
    if len(schedules) == 0: #만약 전체일정리스트에 등록된 일정이 0개라면
        messagebox.showerror("시각화 오류", "시각화할 일정이 없습니다.") #시각화 불가 메시지창띄움
        return #시각화 중단

    dates = [] #날짜들을 저장할 빈 리스트
    counts = [] #날짜별 일정개수를 저장할 빈 리스트

    display_rows, _ = expand_schedules_for_display(schedules)
    for s in display_rows:
        date = s[1]

        if date in dates: #만약 해당 날짜가 이미 dates리스트 안에 있다면
            index = dates.index(date) #해당 날짜가 dates리스트의 몇번째 위치인지 찾음
            counts[index] += 1 #같은 위치의 일정개수를 1 증가
        else: #만약 해당 날짜가 dates리스트 안에 아직 없다면
            dates.append(date) #dates리스트에 새 날짜 추가
            counts.append(1) #counts리스트에 해당 날짜의 일정개수 1 추가

    paired = [] #날짜와 일정개수를 한쌍으로 묶어 저장할 빈 리스트

    for i in range(len(dates)): #dates리스트의 길이만큼 반복
        paired.append([dates[i], counts[i]]) #날짜와 일정개수를 [날짜,개수] 형태로 묶어 paired에 추가

    paired.sort() #날짜와 일정개수 한묶음을 날짜순으로 정렬

    chart_dates = [] #그래프 가로축에 사용할 날짜리스트
    chart_counts = [] #그래프 세로축에 사용할 일정개수리스트

    for p in paired: #정렬된 날짜와 일정개수 한묶음을 하나씩 꺼냄
        chart_dates.append(p[0]) #그래프 날짜리스트에 날짜 추가
        chart_counts.append(p[1]) #그래프 일정개수리스트에 개수 추가

    plt.close("all") #기존에 열려있던 그래프창들을 닫아 그래프창누적을 방지
    plt.figure(figsize=(8, 4)) #가로8 세로4 크기의 새 그래프창 생성
    plt.bar(chart_dates, chart_counts) #날짜별 일정개수 막대그래프 생성
    plt.title("Schedule Count by Date") #그래프 제목 설정
    plt.xlabel("Date") #그래프 가로축 이름 설정
    plt.ylabel("Count") #그래프 세로축 이름 설정
    plt.xticks(rotation=45) #가로축 날짜글자를 45도 회전
    plt.tight_layout() #그래프 제목, 축이름, 날짜글자가 잘리지 않도록 여백 자동조정
    plt.show() #완성된 그래프를 화면에 출력


# ==================== GUI ====================

root = tk.Tk() #메인 프로그램 창 생성
root.title("일정 관리 시스템") #메인창 제목 설정
root.geometry("760x600") #메인창 크기 가로760 세로600으로 설정
root.resizable(False, False) #메인창 크기변경 불가능 설정

title_label = tk.Label(root, text="일정 관리 시스템", font=("Arial", 18, "bold")) #메인창 제목라벨 생성
title_label.pack(pady=10) #제목라벨을 위아래 여백10으로 배치

input_frame = tk.Frame(root) #할일, 날짜, 우선순위, 메모 입력창들을 담을 프레임 생성
input_frame.pack(pady=5) #입력프레임을 위아래 여백5로 배치

tk.Label(input_frame, text="할 일").grid(row=0, column=0, padx=5, pady=5) #할일 안내라벨을 입력프레임 0행0열에 배치
entry_task = tk.Entry(input_frame, width=25) #할 일을 입력받을 입력창 생성
entry_task.grid(row=0, column=1, padx=5, pady=5) #할 일 입력창을 입력프레임 0행1열에 배치
tk.Label(input_frame, text="날짜(YYYY-MM-DD)").grid(row=0, column=2, padx=5, pady=5) #날짜 안내라벨을 입력프레임 0행2열에 배치
entry_date = tk.Entry(input_frame, width=18) #날짜를 입력받을 입력창 생성
entry_date.grid(row=0, column=3, padx=5, pady=5) #날짜 입력창을 입력프레임 0행3열에 배치
entry_date.insert(0, str(datetime.date.today())) #날짜 입력창에 현재시점 오늘날짜 미리 입력

tk.Label(input_frame, text="우선순위").grid(row=1, column=0, padx=5, pady=5) #우선순위 안내라벨을 입력프레임 1행0열에 배치
# 우선순위를 저장할 tkinter 변수 생성
priority_var = tk.StringVar()

# 기본 선택값을 "보통"으로 설정
priority_var.set("보통")

# 드롭다운(OptionMenu) 생성
# 사용자는 긴급 / 높음 / 보통 / 낮음 중 하나 선택 가능
priority_menu = tk.OptionMenu(
    input_frame,
    priority_var,
    "긴급",
    "높음",
    "보통",
    "낮음"
)

# 드롭다운 너비 설정
priority_menu.config(width=20)

# 입력 프레임의 1행 1열 위치에 배치
priority_menu.grid(row=1, column=1, padx=5, pady=5)
tk.Label(input_frame, text="메모").grid(row=1, column=2, padx=5, pady=5) #메모 안내라벨을 입력프레임 1행2열에 배치
entry_memo = tk.Entry(input_frame, width=18) #메모를 입력받을 입력창 생성
entry_memo.grid(row=1, column=3, padx=5, pady=5) #메모 입력창을 입력프레임 1행3열에 배치

tk.Label(input_frame, text="반복 단위").grid(row=2, column=0, padx=5, pady=5)
repeat_var = tk.StringVar(value="매일")
repeat_frame = tk.Frame(input_frame)
repeat_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
tk.Radiobutton(repeat_frame, text="매일", variable=repeat_var, value="매일").pack(side=tk.LEFT)
tk.Radiobutton(repeat_frame, text="매주(7일)", variable=repeat_var, value="매주").pack(side=tk.LEFT, padx=10)
tk.Label(input_frame, text="반복 종료(선택)").grid(row=2, column=2, padx=5, pady=5)
repeat_end_var = tk.StringVar(value="")
make_date_picker(input_frame, repeat_end_var, lambda: entry_date.get()).grid(row=2, column=3, padx=5, pady=5, sticky="w")

button_frame = tk.Frame(root) #버튼들을 담을 프레임 생성
button_frame.pack(pady=8) #버튼프레임을 위아래 여백8로 배치

tk.Button(button_frame, text="일정 추가", width=14, command=add_schedule).grid(row=0, column=0, padx=4, pady=4) #일정추가 버튼을 만들고 add_schedule함수와 연결 후 0행0열에 배치
tk.Button(button_frame, text="반복 일정 추가", width=14, command=add_recurring_schedule).grid(row=2, column=0, padx=4, pady=4)
tk.Button(button_frame, text="전체 보기", width=14, command=show_all).grid(row=0, column=1, padx=4, pady=4) #전체보기 버튼을 만들고 show_all함수와 연결 후 0행1열에 배치
tk.Button(button_frame, text="날짜별 조회", width=14, command=open_date_search_window).grid(row=0, column=2, padx=4, pady=4) #날짜별조회 버튼을 만들고 open_date_search_window함수와 연결 후 0행2열에 배치
tk.Button(button_frame, text="우선순위 정렬", width=14, command=sort_by_priority).grid(row=0, column=3, padx=4, pady=4) #우선순위정렬 버튼을 만들고 sort_by_priority함수와 연결 후 0행3열에 배치

tk.Button(button_frame, text="D-day 계산", width=14, command=open_dday_window).grid(row=1, column=0, padx=4, pady=4) #D-day계산 버튼을 만들고 open_dday_window함수와 연결 후 1행0열에 배치
tk.Button(button_frame, text="선택 삭제", width=14, command=delete_selected).grid(row=1, column=1, padx=4, pady=4) #선택삭제 버튼을 만들고 delete_selected함수와 연결 후 1행1열에 배치
tk.Button(button_frame, text="선택 수정", width=14, command=edit_selected).grid(row=2, column=1, padx=4, pady=4)
tk.Button(button_frame, text="날짜별 시각화", width=14, command=show_date_chart).grid(row=1, column=2, padx=4, pady=4) #날짜별시각화 버튼을 만들고 show_date_chart함수와 연결 후 1행2열에 배치
tk.Button(button_frame, text="초기화", width=14, command=reset_all_schedules).grid(row=1, column=3, padx=4, pady=4) #초기화 버튼을 만들고 reset_all_schedules함수와 연결 후 1행3열에 배치

status_label = tk.Label(root, text="", font=("Arial", 10)) #전체일정개수, 오늘일정개수, 오늘날짜를 보여줄 상태라벨 생성
status_label.pack(pady=5) #상태라벨을 위아래 여백5로 배치

result_frame = tk.Frame(root) #결과창과 스크롤바를 담을 프레임 생성
result_frame.pack(pady=5) #결과프레임을 위아래 여백5로 배치

scrollbar = tk.Scrollbar(result_frame) #결과창에 연결할 세로스크롤바 생성
scrollbar.pack(side=tk.RIGHT, fill=tk.Y) #스크롤바를 오른쪽에 세로방향으로 채워서 배치

result_box = tk.Listbox(result_frame, width=105, height=15, yscrollcommand=scrollbar.set) #일정목록을 보여줄 리스트박스 생성
result_box.pack(side=tk.LEFT) #리스트박스를 결과프레임 왼쪽에 배치

scrollbar.config(command=result_box.yview) #스크롤바를 움직이면 리스트박스 화면도 같이 움직이도록 연결

load_schedules() #프로그램 시작시 파일에서 저장된 일정들을 불러옴
show_all() #불러온 전체일정을 화면에 출력

root.mainloop() #메인창이 꺼지지 않고 계속 실행되도록 함