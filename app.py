import streamlit as st
import re

# Initialize state
if "players" not in st.session_state:
    st.session_state.players = set()
if "num_courts" not in st.session_state:
    st.session_state.num_courts = 3
if "courts" not in st.session_state:
    st.session_state.courts = {i: [] for i in range(1, st.session_state.num_courts + 1)}
if "waitlist" not in st.session_state:
    st.session_state.waitlist = []
if "lesson_court" not in st.session_state:
    st.session_state.lesson_court = []
if "selected_players" not in st.session_state:
    st.session_state.selected_players = set()

st.set_page_config(layout="wide")
st.title("KUBC 코트 Organizer")
st.markdown("---")

# --- Sidebar Configuration ---
st.sidebar.header("코트 관리")
add_court = st.sidebar.button("➕ 코트 추가")
remove_court = st.sidebar.button("➖ 코트 제거")

st.sidebar.markdown("---")
st.sidebar.subheader("인원 추가")
name = st.sidebar.text_input("이름 입력", key="sidebar_name")
if st.sidebar.button("추가", key="sidebar_add") and name:
    in_use = set(p for court in st.session_state.courts.values() for p in court)
    in_waitlist = set(p for team in st.session_state.waitlist for p in team)
    if name in st.session_state.players or name in in_use or name in in_waitlist:
        st.sidebar.warning("이미 존재하는 이름입니다.")
    else:
        st.session_state.players.add(name)
        st.sidebar.success(f"{name}님 명단에 추가되었습니다.")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("인원 일괄 추가")

raw_names_input = st.sidebar.text_area("줄바꿈 또는 띄어쓰기로 구분하여 작성해 주세요", key="bulk_name_input")

if st.sidebar.button("추가", key="bulk_add_button") and raw_names_input.strip():
    # Split by any combination of space, tab, or line break
    names = re.split(r"[ \n\r\t]+", raw_names_input.strip())
    added_names = []
    in_use = set(p for court in st.session_state.courts.values() for p in court)
    in_waitlist = set(p for team in st.session_state.waitlist for p in team)
    
    for name in names:
        name = name.strip()
        if name and name not in st.session_state.players and name not in in_use and name not in in_waitlist:
            st.session_state.players.add(name)
            added_names.append(name)
    
    if added_names:
        st.sidebar.success(f"✅ Added: {', '.join(added_names)}")
        st.rerun()
    else:
        st.sidebar.warning("⚠️ No new names were added (they may already exist).")

# --- Sidebar: Removable Free Players ---
if st.session_state.players:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Free 인원 관리")
    in_use = set(p for court in st.session_state.courts.values() for p in court)
    in_waitlist = set(p for team in st.session_state.waitlist for p in team)
    in_lesson = set(st.session_state.lesson_court)
    removable_players = sorted([p for p in st.session_state.players if p not in in_use and p not in in_waitlist and p not in in_lesson])

    for p in removable_players:
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            st.markdown(f"- {p}")
        with col2:
            if st.button("X", key=f"remove_sidebar_{p}"):
                st.session_state.players.remove(p)
                st.rerun()

if add_court:
    st.session_state.num_courts += 1
    st.session_state.courts[st.session_state.num_courts] = []
    st.rerun()

if remove_court and st.session_state.num_courts > 1:
    court_to_remove = st.session_state.num_courts
    if not st.session_state.courts[court_to_remove]:
        del st.session_state.courts[court_to_remove]
        st.session_state.num_courts -= 1
        st.rerun()
    else:
        st.sidebar.warning(f"{court_to_remove}번 코트는 현재 게임이 진행 중입니다.")

# --- Three-column layout ---
left_col, right_col = st.columns([2, 1])

# --- Left Column: Court Status (including Lesson Court) ---
with left_col:
    st.subheader("\U0001F3F8 코트 현황")
    for i in range(1, st.session_state.num_courts + 1):
        players = st.session_state.courts[i]
        if players:
            st.markdown(f"<h5>{i}번 코트: {', '.join(players)}</h5>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h5>{i}번 코트:</h5>", unsafe_allow_html=True)

        if players and st.button(f"게임 끝내기", key=f"end_game_court_{i}"):
            st.session_state.players.update(st.session_state.courts[i])
            st.session_state.courts[i] = []
            st.success(f"{i}번 코트 게임 마무리 되었습니다.")
            st.rerun()

    st.markdown("---")
    st.markdown(f"<h5>대기열 관리</h5>", unsafe_allow_html=True)

    if st.session_state.waitlist:
        for idx, team in enumerate(st.session_state.waitlist):
            cols = st.columns([3] + [1]*st.session_state.num_courts)
            with cols[0]:
                st.markdown(f"**팀 {idx + 1}:** {', '.join(team)}")
            for court_id, col in zip(range(1, st.session_state.num_courts + 1), cols[1:]):
                with col:
                    if not st.session_state.courts[court_id]:
                        if st.button(f"{court_id}번 코트", key=f"assign_team_{idx}_court_{court_id}"):
                            st.session_state.courts[court_id] = team
                            st.session_state.waitlist.remove(team)
                            st.success(f"{idx + 1}번 팀이 {court_id}번 코트로 배정되었습니다.")
                            st.rerun()
    else:
        st.write("대기중인 팀이 없습니다.")
# --- Right Column: Free Player Selection ---
with right_col:
    st.subheader("\U0001F465 명단")
    st.markdown("---")
    if st.button("대기열 추가", key="add_team_button"):
        if len(st.session_state.selected_players) == 4:
            new_team = list(st.session_state.selected_players)
            st.session_state.waitlist.append(new_team)
            for p in new_team:
                st.session_state.players.remove(p)
            st.session_state.selected_players.clear()
            st.success(f"{new_team}을(를) 대기열에 추가하였습니다.")
            st.rerun()
        else:
            st.warning("정확히 4인을 선택하셔야 합니다.")
    free_players = sorted(list(st.session_state.players))
    if free_players:
        rows = [free_players[i:i+3] for i in range(0, len(free_players), 3)]
        for row in rows:
            cols = st.columns(len(row))
            for idx, p in enumerate(row):
                with cols[idx]:
                    if p in st.session_state.selected_players:
                        if st.button(f"✅ {p}", key=f"free_deselect_{p}"):
                            st.session_state.selected_players.remove(p)
                            st.rerun()
                    else:
                        if st.button(f"➕ {p}", key=f"free_select_{p}"):
                            if len(st.session_state.selected_players) < 4:
                                st.session_state.selected_players.add(p)
                            st.rerun()
    else:
        st.markdown("<i>현재 게임에 참여할 수 있는 인원이 없습니다.</i>", unsafe_allow_html=True)
    st.markdown("---")
    lesson_players = st.session_state.lesson_court
    st.markdown(f"<p><em>레슨 코트:</em></p>", unsafe_allow_html=True)
    if st.session_state.lesson_court:
        btn_cols = st.columns(len(st.session_state.lesson_court))
        for idx, p in enumerate(st.session_state.lesson_court):
            with btn_cols[idx]:
                if st.button(f"{p} X", key=f"remove_lesson_mid_{p}"):
                    st.session_state.lesson_court.remove(p)
                    st.session_state.players.add(p)
                    st.success(f"{p}님이 레슨 코트에서 제거되었습니다.")
                    st.rerun()

    available_for_lesson = sorted(list(st.session_state.players - set(st.session_state.lesson_court)))
    selected_lesson = st.selectbox("레슨 코트에 추가할 인원 선택", ["선택 안 함"] + available_for_lesson, key="lesson_select_unique")
    if selected_lesson != "선택 안 함":
        if len(st.session_state.lesson_court) < 3:
            st.session_state.lesson_court.append(selected_lesson)
            st.session_state.players.remove(selected_lesson)
            st.success(f"{selected_lesson}님이 레슨 코트에 추가되었습니다.")
            st.rerun()
        else:
            st.warning("레슨 코트는 최대 3명 이용 가능합니다.")


st.markdown("---")
st.markdown("<h5>©J1Y2003, last updated 07-07-2025</h5>", unsafe_allow_html=True)