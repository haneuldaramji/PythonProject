# 메인 창 Tkinter 위젯 참조. main.py에서 화면을 만든 뒤 각 변수에 위젯을 연결한다.

root = None  # 메인 애플리케이션 창(Tk)
entry_task = None  # 할 일 입력칸(Entry)
entry_start = None  # 시작일 입력칸(Entry)
entry_end = None  # 종료일 입력칸(Entry)
entry_memo = None  # 메모 입력칸(Entry)
priority_var = None  # 우선순위 콤보박스 값(StringVar)
status_label = None  # 하단 통계 표시 라벨(Label)
result_box = None  # 일정 목록 표시 리스트박스(Listbox)
dday_toggle_btn = None  # 종료일까지 남은 일수 표시 켜기/끄기 버튼(Button)
