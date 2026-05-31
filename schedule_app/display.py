import datetime
import tkinter as tk

from schedule_app import state, ui
from schedule_app.date_utils import make_dday_text

# 결과 리스트박스 표시와 하단 상태 라벨 갱신.


# 하단 상태 라벨에 등록·표시·오늘 일정 개수와 오늘 날짜를 갱신한다.
def update_status():
    today = str(datetime.date.today())
    today_count = sum(1 for s in state.schedules if s[1] <= today <= s[2])
    ui.status_label["text"] = (
        f"등록 일정: {len(state.schedules)}개 | "
        f"화면 표시: {len(state.current_rows)}개 | "
        f"오늘 일정: {today_count}개 | 오늘 날짜: {today}"
    )


# 전달받은 일정 목록을 결과 리스트박스에 번호·기간·우선순위 형식으로 표시한다.
def show_rows(rows, empty_msg, dday_mode):
    state.current_rows.clear()
    ui.result_box.delete(0, tk.END)

    if len(rows) == 0:
        ui.result_box.insert(tk.END, empty_msg)
    else:
        for i, s in enumerate(rows, 1):
            state.current_rows.append(s)
            task, start_date, end_date, priority, memo = s[0], s[1], s[2], s[3], s[4]
            date_display = (
                start_date if start_date == end_date else f"{start_date} ~ {end_date}"
            )
            dday = f"{make_dday_text(end_date)} | " if dday_mode else ""
            memo_part = f" | 메모: {memo}" if memo != "" else ""
            text = f"{i}. {date_display} | {dday}[{priority}] | {task}{memo_part}"
            ui.result_box.insert(tk.END, text)

    update_status()
