from schedule_app.config import PRIORITY_ORDER

# 일정 목록 정렬 시 사용하는 비교 키 함수.


# 시작일 우선, 같은 날짜면 우선순위 순으로 정렬할 때 사용하는 키를 반환한다.
def sort_key_by_date_priority(s):
    return (s[1], PRIORITY_ORDER.get(s[3], 99))


# 우선순위 우선, 같은 단계면 시작일 순으로 정렬할 때 사용하는 키를 반환한다.
def sort_key_by_priority_date(s):
    return (PRIORITY_ORDER.get(s[3], 99), s[1])
