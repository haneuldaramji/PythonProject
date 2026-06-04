import calendar
import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from schedule_app.date_utils import date_to_str
from schedule_app.theme import COLORS, center_toplevel, font, primary_button, style_toplevel

# 기간 선택용 팝업 달력 UI.


# 팝업 달력에서 시작일·종료일을 선택한다.
# on_search가 있으면 두 날짜 선택 후 하단 [조회]로 검색하고, 없으면 두 번째 클릭 시 set_range_func 호출 후 닫는다.
def open_range_calendar(
    parent,
    set_range_func=None,
    on_search=None,
    allow_past=False,
    root=None,
):
    win = tk.Toplevel(parent)
    win.title("시작일을 선택하세요 (1/2)")
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()
    style_toplevel(win, parent)

    theme_root = root or parent.winfo_toplevel()
    view = datetime.date.today()
    cal_state = {"year": view.year, "month": view.month}
    clicks = []
    range_selected = {"start": None, "end": None}

    card = ttk.LabelFrame(win, text="  기간 선택  ", padding=12)
    card.pack(padx=14, pady=14)

    nav = ttk.Frame(card)
    nav.pack(pady=(0, 8))

    title_label = ttk.Label(nav, text="", font=font(parent, 12, True))
    title_label.pack(side=tk.LEFT, padx=10)

    grid_frame = tk.Frame(card, bg=COLORS["card"])
    grid_frame.pack()

    range_label = ttk.Label(card, text="시작일과 종료일을 차례로 선택하세요.", style="Hint.TLabel")

    def apply_range(start_date_obj, end_date_obj):
        if end_date_obj < start_date_obj:
            start_date_obj, end_date_obj = end_date_obj, start_date_obj
        range_selected["start"] = start_date_obj
        range_selected["end"] = end_date_obj
        start_str = date_to_str(start_date_obj)
        end_str = date_to_str(end_date_obj)
        range_label.config(text=f"선택: {start_str} ~ {end_str}")
        if set_range_func is not None:
            set_range_func(start_str, end_str)
        render_days()

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
            range_selected["start"] = None
            range_selected["end"] = None
            range_label.config(text=f"시작: {date_to_str(picked)}  →  종료일을 선택하세요")
            win.title("종료일을 선택하세요 (2/2)")
            render_days()
        elif len(clicks) == 1:
            start_date_obj, end_date_obj = clicks[0], picked
            clicks.clear()
            apply_range(start_date_obj, end_date_obj)
            if on_search is None:
                win.destroy()
            else:
                win.title("기간 선택")

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

        sel_start = range_selected["start"]
        sel_end = range_selected["end"]

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
                state_btn = tk.NORMAL if allow_past or day_date >= today else tk.DISABLED

                in_range = (
                    sel_start is not None
                    and sel_end is not None
                    and sel_start <= day_date <= sel_end
                )
                picking_start = len(clicks) == 1 and day_date == clicks[0]
                selected = in_range or picking_start
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

    def run_search():
        if range_selected["start"] is None or range_selected["end"] is None:
            messagebox.showwarning(
                "선택 필요",
                "시작일과 종료일을 차례로 선택한 뒤 조회를 누르세요.",
                parent=win,
            )
            return
        on_search(
            date_to_str(range_selected["start"]),
            date_to_str(range_selected["end"]),
        )
        win.destroy()

    render_days()
    range_label.pack(pady=(10, 0))

    if on_search is not None:
        ttk.Label(
            card,
            text="1) 시작일  2) 종료일 선택 후 [조회]",
            style="Hint.TLabel",
        ).pack(pady=(6, 0))
        btn_row = ttk.Frame(card)
        btn_row.pack(fill=tk.X, pady=(10, 0))
        primary_button(btn_row, "조회", run_search, theme_root).pack()
        center_toplevel(win, 340, 420)
    else:
        ttk.Label(
            card,
            text="1) 시작일  2) 종료일 클릭  ·  * 오늘  ·  같은 날 두 번 = 하루",
            style="Hint.TLabel",
        ).pack(pady=(6, 0))
        center_toplevel(win, 340, 360)

    win.lift()
    win.focus_force()
