# 일정·날짜·입력 문자열이 규칙에 맞는지 검사하고 오류 안내 문구를 제공한다.

# YYYY-MM-DD 형식 문자열이 실제 존재하는 날짜인지 검사한다.
def is_valid_date(text):
    parts = text.split("-")
    if len(parts) != 3:
        return False

    y, m, d = parts[0], parts[1], parts[2]
    if len(y) != 4 or len(m) != 2 or len(d) != 2:
        return False
    if not (y.isdigit() and m.isdigit() and d.isdigit()):
        return False

    y, m, d = int(y), int(m), int(d)
    if y < 1 or y > 9999 or m < 1 or m > 12:
        return False

    last_days_of_m = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if y % 400 == 0 or (y % 4 == 0 and y % 100 != 0):
        last_days_of_m[1] = 29
    if d < 1 or d > last_days_of_m[m - 1]:
        return False
    return True


# 텍스트에 파일 저장 시 사용하는 | 또는 줄바꿈 문자가 포함되어 있는지 확인한다.
def has_forbidden_char(text):
    return "|" in text or "\n" in text or "\r" in text


# 날짜 입력 형식이 잘못되었을 때 보여줄 안내 문구를 반환한다.
def date_error_message():
    return "날짜는 실제 존재하는 날짜를 YYYY-MM-DD 형식으로 입력하세요. 예: 2026-05-24"


# 금지 문자 사용 시 보여줄 안내 문구를 반환한다.
def forbidden_char_message():
    return "입력란에는 | 문자와 줄바꿈 문자를 사용할 수 없습니다."


# 우선순위 문자열이 허용된 값(긴급·높음·보통·낮음)인지 확인한다.
def valid_priority(priority):
    from schedule_app.config import PRIORITIES
    return priority in PRIORITIES


# 일정 한 행(할일·시작일·종료일·우선순위·메모)이 저장·표시 가능한 형식인지 검사한다.
def is_valid_schedule_row(s):
    if len(s) != 5 or s[0] == "":
        return False
    if has_forbidden_char(s[0]) or has_forbidden_char(s[4]):
        return False
    if not is_valid_date(s[1]) or not is_valid_date(s[2]):
        return False
    if s[1] > s[2]:
        return False
    return valid_priority(s[3])
