import calendar
import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from schedule_app.date_utils import date_to_str
from schedule_app.theme import COLORS, font, style_toplevel

# 기간 선택용 팝업 달력 UI.


# 팝업 달력에서 시작일·종료일을 두 번 클릭해 선택하고 콜백으로 전달한다.
def open_range_calendar(parent, set_range_func):
    win = tk.Toplevel(parent)
    win.title("시작일을 선택하세요 (1/2)")
    win.resizable(False, False)
    win.grab_set()
    style_toplevel(win, parent)

    view = datetime.date.today()
    cal_state = {"year": view.year, "month": view.month}
    clicks = []

    card = ttk.LabelFrame(win, text="  기간 선택  ", padding=12)
    card.pack(padx=14, pady=14)

    nav = ttk.Frame(card)
    nav.pack(pady=(0, 8))

    title_label = ttk.Label(nav, text="", font=font(parent, 12, True))
    title_label.pack(side=tk.LEFT, padx=10)

    grid_frame = tk.Frame(card, bg=COLORS["card"])
    grid_frame.pack()

    def change_month(delta):
        y = cal_state["year"]
        m = cal_state["month"] + delta

        if m < 1:
            m, y = 12, y - 1
        elif m > 12:
            m, y = 1, y + 1

        if y < 1 or y > 9999:
            messagebox.showerror(
                "이동 오류",
                "달력은 0001년부터 9999년까지만 이동할 수 있습니다.",
                parent=win,
            )
            return

        cal_state["year"] = y
        cal_state["month"] = m
        render_days()

    ttk.Button(nav, text="◀", width=4, command=lambda: change_month(-1)).pack(side=tk.LEFT)
    ttk.Button(nav, text="▶", width=4, command=lambda: change_month(1)).pack(side=tk.RIGHT)

    def pick_date(day):
        picked = datetime.date(cal_state["year"], cal_state["month"], day)

        if len(clicks) == 0:
            clicks.append(picked)
            win.title("종료일을 선택하세요 (2/2)")
            render_days()
        elif len(clicks) == 1:
            start_date_obj = clicks[0]
            if picked < start_date_obj:
                messagebox.showerror(
                    "선택 오류",
                    "종료일은 시작일보다 빠를 수 없습니다.",
                    parent=win,
                )
                return
            set_range_func(date_to_str(start_date_obj), date_to_str(picked))
            win.destroy()

    def render_days():
        for child in grid_frame.winfo_children():
            child.destroy()

        y, m = cal_state["year"], cal_state["month"]
        today = datetime.date.today()
        title_label.config(text=f"{y}년 {m}월")

        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for col, name in enumerate(weekdays):
            tk.Label(
                grid_frame,
                text=name,
                width=4,
                font=font(parent, 9, True),
                bg=COLORS["header"],
                fg=COLORS["text"],
            ).grid(row=0, column=col, pady=2, padx=1)

        month_days = calendar.monthcalendar(y, m)
        for row_index, week in enumerate(month_days, start=1):
            for col_index, day in enumerate(week):
                if day == 0:
                    tk.Label(grid_frame, text="", width=4, bg=COLORS["card"]).grid(
                        row=row_index, column=col_index
                    )
                    continue

                day_date = datetime.date(y, m, day)
                btn_text = str(day) + ("*" if day_date == today else "")
                state_btn = tk.NORMAL if day_date >= today else tk.DISABLED
                selected = len(clicks) == 1 and day_date == clicks[0]
                bg = COLORS["primary"] if selected else COLORS["card"]
                fg = COLORS["primary_text"] if selected else COLORS["text"]

                btn = tk.Button(
                    grid_frame,
                    text=btn_text,
                    width=4,
                    state=state_btn,
                    bg=bg,
                    fg=fg,
                    activebackground=COLORS["primary_active"],
                    activeforeground=COLORS["primary_text"],
                    relief=tk.FLAT if selected else tk.RAISED,
                    font=font(parent, 9),
                    command=lambda d=day: pick_date(d),
                )
                btn.grid(row=row_index, column=col_index, padx=1, pady=1)

    render_days()
    ttk.Label(card, text="* 오늘  ·  같은 날짜를 두 번 누르면 하루 일정", style="Hint.TLabel").pack(
        pady=(10, 0)
    )
