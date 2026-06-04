import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from schedule_app import state, ui
from schedule_app.display import show_rows
from schedule_app.sorting import sort_key_by_date_priority
from schedule_app.theme import center_toplevel, primary_button, style_toplevel
from schedule_app.validation import date_error_message, is_valid_date

# 날짜·기간 조회용 팝업 창.


def _filter_by_single_date(target_date):
    return [s for s in state.schedules if s[1] <= target_date <= s[2]]


def _filter_by_range(start_date, end_date):
    return [s for s in state.schedules if s[1] <= end_date and s[2] >= start_date]


def apply_range_search(start_date, end_date):
    filtered = _filter_by_range(start_date, end_date)
    sorted_filtered = sorted(filtered, key=sort_key_by_date_priority)
    show_rows(sorted_filtered, "해당 기간에 포함되는 일정이 없습니다.")


# 날짜 입력 팝업을 띄우고, 해당 날짜에 포함되는 일정만 결과창에 표시한다.
def open_date_search_window():
    win = tk.Toplevel(ui.root)
    win.title("날짜별 조회")
    win.resizable(False, False)
    style_toplevel(win, ui.root)
    center_toplevel(win, 400, 260)

    card = ttk.LabelFrame(win, text="  조회 날짜  ", padding=16)
    card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(16, 8))

    ttk.Label(card, text="해당 날짜에 진행 중인 일정을 표시합니다.").pack(anchor="w", pady=(0, 8))
    ttk.Label(card, text="형식: YYYY-MM-DD  (예: 2026-06-01)", style="Hint.TLabel").pack(
        anchor="w", pady=(0, 10)
    )

    date_entry = ttk.Entry(card, width=24, justify="center")
    date_entry.pack(pady=4)
    date_entry.insert(0, str(datetime.date.today()))
    date_entry.focus_set()

    def run():
        target_date = date_entry.get().strip()
        if not is_valid_date(target_date):
            messagebox.showerror("입력 오류", date_error_message(), parent=win)
            return

        filtered = _filter_by_single_date(target_date)
        sorted_filtered = sorted(filtered, key=sort_key_by_date_priority)
        show_rows(sorted_filtered, "해당 날짜에 포함되는 일정이 없습니다.")
        win.destroy()

    btn_row = ttk.Frame(card)
    btn_row.pack(fill=tk.X, pady=(14, 4))
    confirm = primary_button(btn_row, "확인", run, ui.root)
    confirm.pack()
    win.bind("<Return>", lambda _e: run())
