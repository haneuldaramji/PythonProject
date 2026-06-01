import tkinter as tk
import tkinter.messagebox as messagebox

from schedule_app import state, ui
from schedule_app.display import show_rows
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
    selected = ui.result_box.curselection()
    if len(selected) == 0:
        messagebox.showerror("선택 오류", "삭제할 일정을 먼저 선택하세요.")
        return

    index = selected[0]
    if index >= len(state.current_rows):
        messagebox.showerror("삭제 오류", "삭제할 일정이 없습니다.")
        return

    target = state.current_rows[index]
    if target in state.schedules:
        state.schedules.remove(target)
        if save_schedules():
            show_all()
            ui.result_box.selection_clear(0, tk.END)
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
    selected = ui.result_box.curselection()
    if len(selected) == 0:
        messagebox.showerror("선택 오류", "수정할 일정을 먼저 선택하세요.")
        return

    index = selected[0]
    if index >= len(state.current_rows):
        messagebox.showerror("수정 오류", "수정할 일정이 없습니다.")
        return

    target = state.current_rows[index]
    if target not in state.schedules:
        messagebox.showerror("수정 오류", "수정할 일정을 찾지 못했습니다.")
        return

    win = tk.Toplevel(ui.root)
    win.title("일정 수정")
    win.geometry("460x280")
    win.resizable(False, False)

    frame = tk.Frame(win)
    frame.pack(pady=15)

    tk.Label(frame, text="할 일").grid(row=0, column=0, padx=5, pady=5)
    edit_task = tk.Entry(frame, width=32)
    edit_task.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")
    edit_task.insert(0, target[0])

    tk.Label(frame, text="시작일").grid(row=1, column=0, padx=5, pady=5)
    edit_start = tk.Entry(frame, width=15)
    edit_start.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    edit_start.insert(0, target[1])

    tk.Label(frame, text="종료일").grid(row=2, column=0, padx=5, pady=5)
    edit_end = tk.Entry(frame, width=15)
    edit_end.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    edit_end.insert(0, target[2])

    tk.Label(frame, text="우선순위").grid(row=3, column=0, padx=5, pady=5)
    edit_priority_var = tk.StringVar(value=target[3])
    tk.OptionMenu(frame, edit_priority_var, "긴급", "높음", "보통", "낮음").grid(
        row=3, column=1, padx=5, pady=5, sticky="w"
    )

    tk.Label(frame, text="메모").grid(row=4, column=0, padx=5, pady=5)
    edit_memo = tk.Entry(frame, width=32)
    edit_memo.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="w")
    edit_memo.insert(0, target[4])

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

    tk.Button(win, text="저장", width=12, command=save_edit).pack(pady=5)


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
