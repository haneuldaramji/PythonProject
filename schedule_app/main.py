import datetime
import tkinter as tk

from schedule_app import ui
from schedule_app.calendar_widget import open_range_calendar
from schedule_app.crud import (
    add_schedule,
    delete_selected,
    edit_selected,
    reset_all_schedules,
    show_all,
    sort_by_priority,
)
from schedule_app.display import toggle_dday_display, update_dday_toggle_button
from schedule_app.input_ops import set_main_dates
from schedule_app.search import open_date_search_window
from schedule_app.storage import load_schedules

# 메인 창 UI 구성, 버튼 연결, 프로그램 실행 진입.


# 메인 창 UI를 구성하고 일정을 불러온 뒤 이벤트 루프를 시작한다.
def run():
    ui.root = tk.Tk()
    ui.root.title("일정 관리 시스템 (기간 연속일정)")
    ui.root.geometry("760x600")
    ui.root.resizable(False, False)

    tk.Label(
        ui.root, text="일정 관리 시스템", font=("Arial", 18, "bold")
    ).pack(pady=10)

    input_frame = tk.Frame(ui.root)
    input_frame.pack(pady=5)

    tk.Label(input_frame, text="할 일").grid(row=0, column=0, padx=5, pady=5)
    ui.entry_task = tk.Entry(input_frame, width=25)
    ui.entry_task.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="시작 날짜(YYYY-MM-DD)").grid(
        row=0, column=2, padx=5, pady=5
    )
    ui.entry_start = tk.Entry(input_frame, width=15)
    ui.entry_start.grid(row=0, column=3, padx=5, pady=5)
    ui.entry_start.insert(0, str(datetime.date.today()))

    tk.Button(
        input_frame,
        text="기간 달력",
        width=10,
        command=lambda: open_range_calendar(ui.root, set_main_dates),
    ).grid(row=0, column=4, rowspan=2, padx=8, pady=5, sticky="ns")

    tk.Label(input_frame, text="우선순위").grid(row=1, column=0, padx=5, pady=5)
    ui.priority_var = tk.StringVar(value="보통")
    priority_menu = tk.OptionMenu(
        input_frame, ui.priority_var, "긴급", "높음", "보통", "낮음"
    )
    priority_menu.config(width=20)
    priority_menu.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="종료 날짜(YYYY-MM-DD)").grid(
        row=1, column=2, padx=5, pady=5
    )
    ui.entry_end = tk.Entry(input_frame, width=15)
    ui.entry_end.grid(row=1, column=3, padx=5, pady=5)
    ui.entry_end.insert(0, str(datetime.date.today()))

    tk.Label(input_frame, text="메모").grid(row=2, column=0, padx=5, pady=5)
    ui.entry_memo = tk.Entry(input_frame, width=50)
    ui.entry_memo.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

    button_frame = tk.Frame(ui.root)
    button_frame.pack(pady=8)

    # 2행 × 4열: 빈 칸 없이 기능별로 정렬
    btn_specs = [
        ("일정 추가", add_schedule, 0, 0),
        ("전체 보기", show_all, 0, 1),
        ("우선순위 정렬", sort_by_priority, 0, 2),
        ("날짜별 조회", open_date_search_window, 0, 3),
        ("선택 수정", edit_selected, 1, 1),
        ("선택 삭제", delete_selected, 1, 2),
        ("전체 초기화", reset_all_schedules, 1, 3),
    ]
    for text, cmd, r, c in btn_specs:
        tk.Button(button_frame, text=text, width=14, command=cmd).grid(
            row=r, column=c, padx=3, pady=4
        )

    ui.dday_toggle_btn = tk.Button(
        button_frame,
        text="종료일 표시: 켜기",
        width=14,
        command=toggle_dday_display,
    )
    ui.dday_toggle_btn.grid(row=1, column=0, padx=3, pady=4)
    update_dday_toggle_button()

    ui.status_label = tk.Label(ui.root, text="", font=("Arial", 10))
    ui.status_label.pack(pady=5)

    result_frame = tk.Frame(ui.root)
    result_frame.pack(pady=5)

    scrollbar = tk.Scrollbar(result_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    ui.result_box = tk.Listbox(
        result_frame, width=105, height=15, yscrollcommand=scrollbar.set
    )
    ui.result_box.pack(side=tk.LEFT)
    scrollbar.config(command=ui.result_box.yview)

    load_schedules()
    show_all()
    ui.root.mainloop()


if __name__ == "__main__":
    run()
