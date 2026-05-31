import calendar
import datetime
import tkinter as tk
import tkinter.messagebox as messagebox

from schedule_app.date_utils import date_to_str

# 기간 선택용 팝업 달력 UI.


# 팝업 달력에서 시작일·종료일을 두 번 클릭해 선택하고 콜백으로 전달한다.
def open_range_calendar(parent, set_range_func):
    win = tk.Toplevel(parent)
    win.title("시작일을 선택하세요 (1/2)")
    win.resizable(False, False)
    win.grab_set()

    view = datetime.date.today()
    cal_state = {"year": view.year, "month": view.month}
    clicks = []

    body = tk.Frame(win)
    body.pack(padx=12, pady=10)

    nav = tk.Frame(body)
    nav.pack(pady=(0, 6))

    title_label = tk.Label(nav, text="", font=("Arial", 12, "bold"))
    title_label.pack(side=tk.LEFT, padx=10)

    grid_frame = tk.Frame(body)
    grid_frame.pack()

    # 달력에서 이전/다음 달로 이동하고 날짜 격자를 다시 그린다.
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

    tk.Button(nav, text="<", width=3, command=lambda: change_month(-1)).pack(side=tk.LEFT)
    tk.Button(nav, text=">", width=3, command=lambda: change_month(1)).pack(side=tk.RIGHT)

    # 클릭한 날짜를 시작일·종료일로 순서대로 받아 검증 후 콜백을 호출하고 창을 닫는다.
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

    # 현재 연·월의 요일 헤더와 날짜 버튼 격자를 화면에 그린다.
    def render_days():
        for child in grid_frame.winfo_children():
            child.destroy()

        y, m = cal_state["year"], cal_state["month"]
        today = datetime.date.today()
        title_label.config(text=f"{y}년 {m}월")

        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for col, name in enumerate(weekdays):
            tk.Label(grid_frame, text=name, width=4).grid(row=0, column=col, pady=2)

        month_days = calendar.monthcalendar(y, m)
        for row_index, week in enumerate(month_days, start=1):
            for col_index, day in enumerate(week):
                if day == 0:
                    tk.Label(grid_frame, text="", width=4).grid(
                        row=row_index, column=col_index
                    )
                    continue

                day_date = datetime.date(y, m, day)
                btn_text = str(day) + ("*" if day_date == today else "")
                state_btn = tk.NORMAL if day_date >= today else tk.DISABLED

                btn = tk.Button(
                    grid_frame,
                    text=btn_text,
                    width=4,
                    state=state_btn,
                    command=lambda d=day: pick_date(d),
                )
                if len(clicks) == 1 and day_date == clicks[0]:
                    btn.config(bg="lightblue", relief=tk.SUNKEN, bd=3)
                btn.grid(row=row_index, column=col_index, padx=1, pady=1)

    render_days()
    tk.Label(body, text="* 오늘 날짜", font=("Arial", 9)).pack(pady=(6, 2))
    tk.Label(body, text="파란색/눌림 표시: 선택한 시작일", font=("Arial", 9)).pack(pady=(0, 2))
    tk.Label(body, text="단일 일정은 같은 날짜를 두 번 누르세요.", font=("Arial", 9)).pack(
        pady=(0, 4)
    )
