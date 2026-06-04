import datetime
import tkinter as tk
from tkinter import ttk

from schedule_app import ui
from schedule_app.calendar_widget import open_range_calendar
from schedule_app.config import PRIORITIES
from schedule_app.crud import (
    add_schedule,
    delete_selected,
    edit_selected,
    reset_all_schedules,
    show_all,
    sort_by_priority,
)
from schedule_app.display import (
    TREE_COLUMNS,
    configure_tree_tags,
    toggle_dday_display,
    update_dday_toggle_button,
)
from schedule_app.input_ops import set_main_dates
from schedule_app.search import open_date_search_window
from schedule_app.storage import load_schedules
from schedule_app.theme import COLORS, apply_theme, font

# 메인 창 UI 구성, 버튼 연결, 프로그램 실행 진입.


# 메인 창 UI를 구성하고 일정을 불러온 뒤 이벤트 루프를 시작한다.
def run():
    ui.root = tk.Tk()
    apply_theme(ui.root)
    ui.root.title("일정 관리 시스템")
    ui.root.geometry("860x580")
    ui.root.minsize(820, 520)

    outer = ttk.Frame(ui.root, padding=12)
    outer.pack(fill=tk.BOTH, expand=True)

    header = ttk.Frame(outer)
    header.pack(fill=tk.X, pady=(0, 8))
    ttk.Label(header, text="일정 관리", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        header,
        text="기간 일정을 등록하고 조회·수정할 수 있습니다.",
        style="Subtitle.TLabel",
    ).pack(anchor="w", pady=(2, 0))

    input_card = ttk.LabelFrame(outer, text="  새 일정  ", padding=10)
    input_card.pack(fill=tk.X, pady=(0, 8))

    today = str(datetime.date.today())

    ttk.Label(input_card, text="할 일").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
    ui.entry_task = ttk.Entry(input_card, width=28)
    ui.entry_task.grid(row=0, column=1, sticky="ew", pady=6)

    ttk.Label(input_card, text="시작일").grid(row=0, column=2, sticky="w", padx=(16, 8), pady=6)
    ui.entry_start = ttk.Entry(input_card, width=14, justify="center")
    ui.entry_start.grid(row=0, column=3, pady=6)
    ui.entry_start.insert(0, today)

    ttk.Label(input_card, text="종료일").grid(row=1, column=2, sticky="w", padx=(16, 8), pady=6)
    ui.entry_end = ttk.Entry(input_card, width=14, justify="center")
    ui.entry_end.grid(row=1, column=3, pady=6)
    ui.entry_end.insert(0, today)

    cal_btn = ttk.Button(
        input_card,
        text="기간 달력",
        width=10,
        command=lambda: open_range_calendar(ui.root, set_main_dates),
    )
    cal_btn.grid(row=0, column=4, rowspan=2, padx=(12, 0), pady=6, sticky="ns")

    ttk.Label(input_card, text="우선순위").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=6)
    ui.priority_var = tk.StringVar(value="보통")
    ui.priority_combo = ttk.Combobox(
        input_card,
        textvariable=ui.priority_var,
        values=PRIORITIES,
        state="readonly",
        width=26,
    )
    ui.priority_combo.grid(row=1, column=1, sticky="ew", pady=6)

    ttk.Label(input_card, text="메모").grid(row=2, column=0, sticky="nw", padx=(0, 8), pady=6)
    ui.entry_memo = ttk.Entry(input_card, width=50)
    ui.entry_memo.grid(row=2, column=1, columnspan=3, sticky="ew", pady=6)

    ttk.Label(
        input_card,
        text="날짜 형식: YYYY-MM-DD (예: 2026-06-01)",
        style="Hint.TLabel",
    ).grid(row=3, column=1, columnspan=3, sticky="w", pady=(0, 2))

    input_card.columnconfigure(1, weight=1)

    action_card = ttk.LabelFrame(outer, text="  작업  ", padding=10)
    action_card.pack(fill=tk.X, pady=(0, 8))

    for col in range(4):
        action_card.columnconfigure(col, weight=1, uniform="action_btn")

    btn_specs = [
        ("일정 추가", add_schedule, "Primary.TButton", 0, 0),
        ("전체 보기", show_all, "TButton", 0, 1),
        ("우선순위 정렬", sort_by_priority, "TButton", 0, 2),
        ("날짜별 조회", open_date_search_window, "TButton", 0, 3),
        ("종료일 표시 켜기", toggle_dday_display, "Toggle.TButton", 1, 0),
        ("선택 수정", edit_selected, "TButton", 1, 1),
        ("선택 삭제", delete_selected, "Danger.TButton", 1, 2),
        ("전체 초기화", reset_all_schedules, "Danger.TButton", 1, 3),
    ]
    btn_char_width = 18
    for text, cmd, style, r, c in btn_specs:
        btn = ttk.Button(
            action_card, text=text, command=cmd, style=style, width=btn_char_width
        )
        btn.grid(row=r, column=c, padx=4, pady=4, sticky="ew")
        if style == "Toggle.TButton":
            ui.dday_toggle_btn = btn

    update_dday_toggle_button()

    list_card = ttk.LabelFrame(outer, text="  일정 목록  ", padding=10)
    list_card.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

    list_inner = tk.Frame(list_card, bg=COLORS["card"])
    list_inner.pack(fill=tk.BOTH, expand=True)

    scroll_y = ttk.Scrollbar(list_inner, orient=tk.VERTICAL)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    ui.result_tree = ttk.Treeview(
        list_inner,
        columns=TREE_COLUMNS,
        show="headings",
        height=10,
        yscrollcommand=scroll_y.set,
        selectmode="browse",
    )
    ui.result_tree.heading("task", text="할 일", anchor="w")
    ui.result_tree.heading("period", text="기간", anchor="center")
    ui.result_tree.heading("priority", text="우선순위", anchor="center")
    ui.result_tree.heading("days", text="종료까지", anchor="center")
    ui.result_tree.heading("memo", text="메모", anchor="w")

    ui.result_tree.column("task", width=220, minwidth=120, anchor="w")
    ui.result_tree.column("period", width=200, minwidth=140, anchor="center")
    ui.result_tree.column("priority", width=72, minwidth=60, anchor="center")
    ui.result_tree.column("days", width=0, minwidth=0, stretch=False, anchor="center")
    ui.result_tree.column("memo", width=280, minwidth=100, anchor="w")

    ui.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_y.config(command=ui.result_tree.yview)

    ui.list_empty_label = tk.Label(
        list_inner,
        text="",
        font=font(ui.root, 11),
        fg=COLORS["muted"],
        bg=COLORS["card"],
    )

    configure_tree_tags()

    status_bar = tk.Frame(outer, bg=COLORS["header"], highlightthickness=1, highlightbackground=COLORS["border"])
    status_bar.pack(fill=tk.X)
    ui.status_label = ttk.Label(status_bar, text="", style="Status.TLabel")
    ui.status_label.pack(fill=tk.X)

    load_schedules()
    show_all()
    ui.root.mainloop()


if __name__ == "__main__":
    run()
