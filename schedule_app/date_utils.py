import datetime

# 날짜 문자열 변환 및 D-day 계산 유틸리티.

# YYYY-MM-DD 문자열을 datetime.date 객체로 변환한다.
def parse_date_str(text):
    parts = text.split("-")
    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))


# datetime.date 객체를 YYYY-MM-DD 문자열로 변환한다.
def date_to_str(d):
    return d.isoformat()


# target_date(보통 일정 종료일)까지 오늘 기준 남은 일수를 D-N, D-Day, D+N 문자열로 만든다.
def make_dday_text(target_date):
    target = parse_date_str(target_date)
    diff = (target - datetime.date.today()).days
    if diff > 0:
        return f"D-{diff}"
    if diff == 0:
        return "D-Day"
    return f"D+{abs(diff)}"
