import datetime

# 날짜 문자열 변환 및 D-day 계산 유틸리티.

# YYYY-MM-DD 문자열을 datetime.date 객체로 변환한다.
def parse_date_str(text):
    parts = text.split("-")
    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))


# datetime.date 객체를 YYYY-MM-DD 문자열로 변환한다.
def date_to_str(d):
    return d.isoformat()


# 종료일까지 남은 일수를 목록 표시용 문구로 만든다.
def make_days_until_end_text(end_date):
    target = parse_date_str(end_date)
    diff = (target - datetime.date.today()).days
    if diff > 0:
        return f"종료까지 {diff}일"
    if diff == 0:
        return "종료일 오늘"
    return f"종료 {abs(diff)}일 지남"
