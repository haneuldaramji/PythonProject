import tkinter as tk
from tkinter import messagebox, ttk

from schedule_app import state, ui
from schedule_app.config import PRIORITIES
from schedule_app.display import clear_selection, get_selected_schedule, show_rows
from schedule_app.theme import style_toplevel
from schedule_app.input_ops import clear_input_fields, read_input_schedule
from schedule_app.sorting import sort_key_by_date_priority, sort_key_by_priority_date
from schedule_app.storage import load_schedules, save_schedules
from schedule_app.validation import (
    date_error_message,
    forbidden_char_message,
    has_forbidden_char,
    is_valid_date,
    valid_priority,
)

# 일정 추가·조회·수정·삭제·초기화 등 CRUD 기능.


# 파일 저장 실패 시 디스크 내용으로 메모리·화면을 되돌린다.
def _reload_after_save_failure():
    load_schedules()
    show_all()


# 전체 일정을 시작일·우선순위 순으로 정렬해 결과창에 표시한다.
def show_all():
    sorted_rows = sorted(state.schedules, key=sort_key_by_date_priority)
    show_rows(sorted_rows, "등록된 일정이 없습니다.")


# 전체 일정을 우선순위·시작일 순으로 정렬해 결과창에 표시한다.
def sort_by_priority():
    sorted_rows = sorted(state.schedules, key=sort_key_by_priority_date)
    show_rows(sorted_rows, "등록된 일정이 없습니다.")


# 입력란에서 일정을 읽어 목록에 추가하고 파일에 저장한 뒤 화면을 갱신한다.
def add_schedule():
    new_schedule = read_input_schedule()
    if new_schedule is None:
        return
    state.schedules.append(new_schedule)
    if save_schedules():
        clear_input_fields()
        show_all()
    else:
        _reload_after_save_failure()


# 결과창에서 선택한 일정을 목록·파일에서 삭제한다.
def delete_selected():
    target = get_selected_schedule()
    if target is None:
        messagebox.showerror("선택 오류", "삭제할 일정을 먼저 선택하세요.")
        return
    if target in state.schedules:
        state.schedules.remove(target)
        if save_schedules():
            show_all()
            clear_selection()
            messagebox.showinfo("삭제 완료", "선택한 일정이 삭제되었습니다.")
        else:
            _reload_after_save_failure()
            messagebox.showerror(
                "삭제 오류", "파일에 저장하지 못해 삭제가 반영되지 않았습니다."
            )
    else:
        messagebox.showerror("삭제 오류", "삭제할 일정을 찾지 못했습니다.")


# 선택한 일정을 수정하는 팝업 창을 열고 저장 시 목록·파일을 갱신한다.
def edit_selected():
    target = get_selected_schedule()
    if target is None:
        messagebox.showerror("선택 오류", "수정할 일정을 먼저 선택하세요.")
        return
    if target not in state.schedules:
        messagebox.showerror("수정 오류", "수정할 일정을 찾지 못했습니다.")
        return

    win = tk.Toplevel(ui.root)
    win.title("일정 수정")
    win.geometry("480x320")
    win.resizable(False, False)
    style_toplevel(win, ui.root)

    card = ttk.LabelFrame(win, text="  일정 수정  ", padding=16)
    card.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    ttk.Label(card, text="할 일").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
    edit_task = ttk.Entry(card, width=36)
    edit_task.grid(row=0, column=1, sticky="ew", pady=6)
    edit_task.insert(0, target[0])

    ttk.Label(card, text="시작일").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
    edit_start = ttk.Entry(card, width=18, justify="center")
    edit_start.grid(row=1, column=1, sticky="w", pady=6)
    edit_start.insert(0, target[1])

    ttk.Label(card, text="종료일").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=6)
    edit_end = ttk.Entry(card, width=18, justify="center")
    edit_end.grid(row=2, column=1, sticky="w", pady=6)
    edit_end.insert(0, target[2])

    ttk.Label(card, text="우선순위").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=6)
    edit_priority_var = tk.StringVar(value=target[3])
    ttk.Combobox(
        card,
        textvariable=edit_priority_var,
        values=PRIORITIES,
        state="readonly",
        width=34,
    ).grid(row=3, column=1, sticky="ew", pady=6)

    ttk.Label(card, text="메모").grid(row=4, column=0, sticky="w", padx=(0, 10), pady=6)
    edit_memo = ttk.Entry(card, width=36)
    edit_memo.grid(row=4, column=1, sticky="ew", pady=6)
    edit_memo.insert(0, target[4])
    card.columnconfigure(1, weight=1)

    # 수정 창 입력값을 검증한 뒤 해당 일정을 교체·저장하고 창을 닫는다.
    def save_edit():
        task = edit_task.get().strip()
        start_date = edit_start.get().strip()
        end_date = edit_end.get().strip()
        priority = edit_priority_var.get()
        memo = edit_memo.get().strip()

        if task == "":
            messagebox.showerror("입력 오류", "할 일을 입력하세요.", parent=win)
            return
        if has_forbidden_char(task) or has_forbidden_char(memo):
            messagebox.showerror("입력 오류", forbidden_char_message(), parent=win)
            return
        if not is_valid_date(start_date):
            messagebox.showerror("입력 오류", "시작 " + date_error_message(), parent=win)
            return
        if not is_valid_date(end_date):
            messagebox.showerror("입력 오류", "종료 " + date_error_message(), parent=win)
            return
        if start_date > end_date:
            messagebox.showerror(
                "입력 오류", "종료일은 시작일보다 빠를 수 없습니다.", parent=win
            )
            return
        if not valid_priority(priority):
            messagebox.showerror(
                "입력 오류", "올바른 우선순위를 선택하세요.", parent=win
            )
            return

        new_item = [task, start_date, end_date, priority, memo]
        if new_item != target and new_item in state.schedules:
            messagebox.showerror(
                "입력 오류", "이미 완전히 동일하게 등록된 일정이 있습니다.", parent=win
            )
            return
        if target not in state.schedules:
            messagebox.showerror("수정 오류", "수정할 일정을 찾지 못했습니다.", parent=win)
            return

        idx = state.schedules.index(target)
        state.schedules[idx] = new_item
        if save_schedules():
            show_all()
            win.destroy()
            messagebox.showinfo("수정 완료", "일정이 수정되었습니다.")
        else:
            _reload_after_save_failure()
            messagebox.showerror(
                "수정 오류",
                "파일에 저장하지 못해 수정이 반영되지 않았습니다.",
                parent=win,
            )

    ttk.Button(win, text="저장", style="Primary.TButton", command=save_edit).pack(pady=(0, 12))


# 사용자 확인 후 모든 일정을 삭제하고 파일·화면을 비운다.
def reset_all_schedules():
    if messagebox.askyesno("초기화 확인", "등록된 모든 일정을 삭제하시겠습니까?"):
        state.schedules.clear()
        state.current_rows.clear()
        if save_schedules():
            clear_input_fields()
            show_all()
        else:
            _reload_after_save_failure()
            messagebox.showerror(
                "초기화 오류", "파일에 저장하지 못해 초기화가 반영되지 않았습니다."
            )
