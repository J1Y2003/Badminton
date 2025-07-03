import streamlit as st

# Initialize state
if "players" not in st.session_state:
    st.session_state.players = set()
if "num_courts" not in st.session_state:
    st.session_state.num_courts = 3
if "courts" not in st.session_state:
    st.session_state.courts = {i: [] for i in range(1, st.session_state.num_courts + 1)}
if "waitlist" not in st.session_state:
    st.session_state.waitlist = []

st.title("KUBC 코트 Organizer")
st.markdown("---")

# --- Court Configuration ---
st.sidebar.header("코트 관리")
add_court = st.sidebar.button("➕ 코트 추가")
remove_court = st.sidebar.button("➖ 코트 제거")

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

# --- Court Status ---
st.subheader("\U0001F3F8 코트 현황")
for i in range(1, st.session_state.num_courts + 1):
    players = st.session_state.courts[i]
    if players:
        st.markdown(f"<h4>{i}번 코트: {', '.join(players)}</h4>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h4>{i}번 코트: </h4>", unsafe_allow_html=True)

    # Button to clear court
    if players and st.button(f"게임 끝내기", key=f"end_game_court_{i}"):
        st.session_state.players.update(st.session_state.courts[i])
        st.session_state.courts[i] = []
        st.success(f"{i}번 코트 게임 마무리 되었습니다.")
        st.rerun()

# --- Create Waitlist Teams ---
st.markdown("---")
st.subheader("\U0001F465 팀 꾸리기")
wait_selected = st.multiselect(
    "게임에 함께하실 4인을 선택해 주세요",
    sorted(st.session_state.players),
    key="waitlist_select",
)

if st.button("대기열 추가"):
    if len(wait_selected) == 4:
        st.session_state.waitlist.append(wait_selected)
        for p in wait_selected:
            st.session_state.players.remove(p)
        st.success(f"{wait_selected}을(를) 대기열에 추가하였습니다.")
        st.rerun()
    else:
        st.warning("코트 당 4인을 선택하셔야 합니다")

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
                        st.success(f"{idx + 1}번 팀 {court_id}번 코트로 배정되었습니다.")
                        st.rerun()
else:
    st.write("대기중인 팀이 없습니다.")

# --- Player Pool ---
st.markdown("---")
st.subheader("Free 인원")

# Remove player logic
if st.session_state.players:
    removable_players = []
    in_use = set(p for court in st.session_state.courts.values() for p in court)
    in_waitlist = set(p for team in st.session_state.waitlist for p in team)

    for p in sorted(st.session_state.players):
        if p not in in_use and p not in in_waitlist:
            removable_players.append(p)

    for p in sorted(st.session_state.players):
        cols = st.columns([4, 1])
        with cols[0]:
            st.markdown(f"- {p}")
        with cols[1]:
            if p in removable_players:
                if st.button("X", key=f"remove_{p}"):
                    st.session_state.players.remove(p)
                    st.success(f"{p}을(를) 명단에서 제거하였습니다.")
                    st.rerun()
else:
    st.write("명단에 사람이 없습니다.")


name = st.text_input("명단에 추가")
if st.button("추가") and name:
    in_use = set(p for court in st.session_state.courts.values() for p in court)
    in_waitlist = set(p for team in st.session_state.waitlist for p in team)
    if name in st.session_state.players or name in in_use or name in in_waitlist:
        st.warning("이미 존재하는 이름입니다.")
    else:
        st.session_state.players.add(name)
        st.success(f"{name}님 명단에 추가되었습니다.")
    st.rerun()