import csv
import os
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

from schedule_app import state
from schedule_app.sorting import sort_key_by_date_priority

# 일정 목록을 CSV 파일로 보내기.


# 전체 일정을 CSV 파일로 저장하고, 원하면 저장한 파일을 연다.
def export_to_csv():
    if len(state.schedules) == 0:
        messagebox.showerror("CSV 저장 오류", "저장할 일정이 없습니다.")
        return

    csv_file = filedialog.asksaveasfilename(
        title="CSV 파일 저장 위치 선택",
        defaultextension=".csv",
        filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")],
        initialfile="schedules.csv",
    )
    if csv_file == "":
        return

    try:
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["할 일", "시작일", "종료일", "우선순위", "메모"])
            sorted_schedules = sorted(state.schedules, key=sort_key_by_date_priority)
            for s in sorted_schedules:
                writer.writerow(s)

        answer = messagebox.askyesno(
            "CSV 저장 완료", "CSV 파일이 저장되었습니다.\n지금 열어보시겠습니까?"
        )
        if answer:
            try:
                if hasattr(os, "startfile"):
                    os.startfile(csv_file)
                else:
                    messagebox.showinfo(
                        "파일 열기 안내",
                        "CSV 파일은 저장되었지만 이 운영체제에서는 자동 열기를 지원하지 않습니다.\n"
                        "저장 위치에서 직접 열어주세요.",
                    )
            except Exception as e:
                messagebox.showerror(
                    "파일 열기 오류",
                    f"CSV 파일은 저장되었지만 자동으로 열지 못했습니다.\n{e}",
                )
    except Exception as e:
        messagebox.showerror(
            "CSV 저장 오류", f"CSV 파일 저장 중 오류가 발생했습니다.\n{e}"
        )
