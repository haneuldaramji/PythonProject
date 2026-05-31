import datetime
import tkinter as tk
import tkinter.messagebox as messagebox

from schedule_app import state, ui
from schedule_app.validation import (
    date_error_message,
    forbidden_char_message,
    has_forbidden_char,
    is_valid_date,
    valid_priority,
)

# 메인 화면 입력칸 읽기·초기화·날짜 설정.


# 메인 화면의 시작일·종료일 입력칸에 지정한 날짜 문자열을 넣는다.
def set_main_dates(start_str, end_str):
    ui.entry_start.delete(0, tk.END)
    ui.entry_start.insert(0, start_str)
    ui.entry_end.delete(0, tk.END)
    ui.entry_end.insert(0, end_str)


# 할일·메모 입력칸을 비우고 날짜·우선순위를 오늘·보통으로 초기화한다.
def clear_input_fields():
    ui.entry_task.delete(0, tk.END)
    today_str = str(datetime.date.today())
    set_main_dates(today_str, today_str)
    ui.priority_var.set("보통")
    ui.entry_memo.delete(0, tk.END)


# 메인 입력란 값을 읽어 검증 후 일정 리스트를 반환하거나 오류 시 None을 반환한다.
def read_input_schedule():
    task = ui.entry_task.get().strip()
    start_date = ui.entry_start.get().strip()
    end_date = ui.entry_end.get().strip()
    priority = ui.priority_var.get()
    memo = ui.entry_memo.get().strip()

    if task == "":
        messagebox.showerror("입력오류", "할 일을 입력하세요.")
        return None
    if has_forbidden_char(task) or has_forbidden_char(memo):
        messagebox.showerror("입력오류", forbidden_char_message())
        return None
    if not is_valid_date(start_date):
        messagebox.showerror("입력 오류", "시작 " + date_error_message())
        return None
    if not is_valid_date(end_date):
        messagebox.showerror("입력 오류", "종료 " + date_error_message())
        return None

    today = str(datetime.date.today())
    if start_date < today or end_date < today:
        messagebox.showerror("입력 오류", "오늘 이전 날짜는 등록할 수 없습니다.")
        return None
    if start_date > end_date:
        messagebox.showerror("입력 오류", "종료일은 시작일보다 빠를 수 없습니다.")
        return None
    if not valid_priority(priority):
        messagebox.showerror("입력 오류", "올바른 우선순위를 선택하세요.")
        ui.priority_var.set("보통")
        return None

    new_schedule = [task, start_date, end_date, priority, memo]
    if new_schedule in state.schedules:
        messagebox.showerror("입력 오류", "이미 완전히 동일하게 등록된 일정이 있습니다.")
        return None
    return new_schedule
