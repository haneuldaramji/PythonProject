import datetime

from schedule_app import state, ui
from schedule_app.date_utils import make_days_until_end_text
from schedule_app.theme import PRIORITY_ROW_COLORS, priority_tag

# 결과 Treeview 표시와 하단 상태 라벨 갱신.

TREE_COLUMNS = ("task", "period", "priority", "days", "memo")


# 하단 상태 라벨에 등록·표시·오늘 일정 개수와 오늘 날짜를 갱신한다.
def update_status():
    today = str(datetime.date.today())
    today_count = sum(1 for s in state.schedules if s[1] <= today <= s[2])
    dday_hint = "켜짐" if state.show_dday else "꺼짐"
    ui.status_label.config(
        text=(
            f"  등록 {len(state.schedules)}건  ·  "
            f"표시 {len(state.current_rows)}건  ·  "
            f"오늘 {today_count}건  ·  "
            f"종료일 표시 {dday_hint}  ·  "
            f"{today}"
        )
    )


# D-day 토글 버튼 문구를 현재 표시 상태에 맞게 갱신한다.
def update_dday_toggle_button():
    if ui.dday_toggle_btn is not None:
        text = "종료일 표시 끄기" if state.show_dday else "종료일 표시 켜기"
        ui.dday_toggle_btn.config(text=text)


# 목록의 종료일까지 남은 일수 표시를 켜거나 끄고, 현재 목록을 다시 그린다.
def toggle_dday_display():
    state.show_dday = not state.show_dday
    update_dday_toggle_button()
    _sync_days_column()
    show_rows(state.last_list_rows, state.last_empty_msg)


# 종료일 열 표시 여부를 토글 상태에 맞게 조정한다.
def _sync_days_column():
    if ui.result_tree is None:
        return
    if state.show_dday:
        ui.result_tree.column("days", width=108, minwidth=80, stretch=False)
    else:
        ui.result_tree.column("days", width=0, minwidth=0, stretch=False)


# Treeview에서 선택된 일정 행을 반환하거나 없으면 None.
def get_selected_schedule():
    if ui.result_tree is None:
        return None
    selected = ui.result_tree.selection()
    if not selected:
        return None
    index = ui.result_tree.index(selected[0])
    if index >= len(state.current_rows):
        return None
    return state.current_rows[index]


# Treeview 선택을 해제한다.
def clear_selection():
    if ui.result_tree is None:
        return
    for item in ui.result_tree.selection():
        ui.result_tree.selection_remove(item)


# 전달받은 일정 목록을 Treeview에 표시한다.
def show_rows(rows, empty_msg):
    state.last_list_rows = rows
    state.last_empty_msg = empty_msg
    state.current_rows.clear()

    tree = ui.result_tree
    tree.delete(*tree.get_children())

    if len(rows) == 0:
        ui.list_empty_label.config(text=empty_msg)
        ui.list_empty_label.place(relx=0.5, rely=0.5, anchor="center")
    else:
        ui.list_empty_label.place_forget()
        for s in rows:
            state.current_rows.append(s)
            task, start_date, end_date, priority, memo = s[0], s[1], s[2], s[3], s[4]
            period = (
                start_date if start_date == end_date else f"{start_date} ~ {end_date}"
            )
            days = make_days_until_end_text(end_date) if state.show_dday else ""
            tree.insert(
                "",
                "end",
                values=(task, period, priority, days, memo if memo else "—"),
                tags=(priority_tag(priority),),
            )

    update_status()


# Treeview 행 배경색(우선순위별)을 설정한다.
def configure_tree_tags():
    tree = ui.result_tree
    for tag, color in PRIORITY_ROW_COLORS.items():
        tree.tag_configure(tag, background=color)
