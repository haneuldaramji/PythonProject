import os
import tkinter.messagebox as messagebox

from schedule_app import state
from schedule_app.config import FILE_NAME
from schedule_app.validation import is_valid_date, is_valid_schedule_row

# schedules.txt 파일에서 일정을 불러오고 저장한다.


# schedules.txt 파일에서 일정 목록을 읽어 메모리(schedules)에 불러온다.
def load_schedules():
    state.schedules.clear()
    skipped_count = 0

    try:
        open(FILE_NAME, "a", encoding="utf-8").close()

        with open(FILE_NAME, "r", encoding="utf-8") as f:
            for line in f:
                data = line.strip().split("|")
                row = None

                if len(data) == 5:
                    row = [data[0], data[1], data[2], data[3], data[4]]
                elif len(data) == 4:
                    row = [data[0], data[1], data[1], data[2], data[3]]
                elif len(data) > 5:
                    end_d = data[5] if len(data) > 5 and is_valid_date(data[5]) else data[1]
                    row = [data[0], data[1], end_d, data[2], data[3]]

                if row is not None and is_valid_schedule_row(row):
                    state.schedules.append(row)
                elif line.strip() != "":
                    skipped_count += 1

        if skipped_count > 0:
            messagebox.showwarning(
                "파일 읽기 경고",
                f"저장 파일에서 형식이 맞지 않는 일정 {skipped_count}개를 건너뛰었습니다.",
            )
    except Exception as e:
        messagebox.showerror(
            "파일 읽기 오류",
            f"저장된 일정 파일을 불러오는 중 오류가 발생했습니다.\n{e}",
        )


# 메모리의 일정 목록을 임시 파일에 쓴 뒤 schedules.txt로 안전하게 저장한다.
def save_schedules():
    temp_file_name = FILE_NAME + ".tmp"

    try:
        with open(temp_file_name, "w", encoding="utf-8") as f:
            for s in state.schedules:
                if is_valid_schedule_row(s):
                    f.write("|".join(s) + "\n")

        os.replace(temp_file_name, FILE_NAME)
        return True
    except Exception as e:
        if os.path.exists(temp_file_name):
            try:
                os.remove(temp_file_name)
            except Exception:
                pass
        messagebox.showerror(
            "파일 저장 오류",
            f"일정 파일을 저장하는 중 오류가 발생했습니다.\n{e}",
        )
        return False
