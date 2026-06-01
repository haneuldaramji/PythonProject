import datetime
import tkinter as tk
import tkinter.messagebox as messagebox

from schedule_app import state, ui
from schedule_app.display import show_rows
from schedule_app.sorting import sort_key_by_date_priority
from schedule_app.validation import date_error_message, is_valid_date

# 날짜별 조회용 팝업 창.


# 날짜 입력 팝업을 띄우고, 해당 날짜에 포함되는 일정만 결과창에 표시한다.
def open_date_search_window():
    win = tk.Toplevel(ui.root)
    win.title("날짜별 조회")
    win.geometry("360x170")
    win.resizable(False, False)

    tk.Label(
        win, text="조회할 날짜를 입력하세요.", font=("Arial", 11, "bold")
    ).pack(pady=8)
    tk.Label(win, text="형식: YYYY-MM-DD  예: 2026-05-11").pack()

    date_entry = tk.Entry(win, width=22, justify="center")
    date_entry.pack(pady=8)
    date_entry.insert(0, str(datetime.date.today()))

    # 입력한 날짜로 일정을 필터링해 정렬·표시하고 팝업 창을 닫는다.
    def run():
        target_date = date_entry.get().strip()
        if not is_valid_date(target_date):
            messagebox.showerror("입력 오류", date_error_message(), parent=win)
            return

        filtered = [s for s in state.schedules if s[1] <= target_date <= s[2]]
        sorted_filtered = sorted(filtered, key=sort_key_by_date_priority)
        show_rows(sorted_filtered, "해당 날짜에 포함되는 일정이 없습니다.")
        win.destroy()

    tk.Button(win, text="조회", width=12, command=run).pack(pady=5)
