import streamlit as st
import sqlite3
from datetime import date
import os

from weather import get_current_weather
from log_event import log_event
from today import get_season, fetch_due_tasks, format_explanation


from ai_context import get_plant_context_bundle
from ai_client import generate_plant_story, PROMPT_VERSION, MODEL_ID_DEFAULT


#---------Helpers-----------

DB_PATH = "plants.db"

st.set_page_config(page_title="Plant Care Dashboard", layout="wide")

st.markdown(
    """
    <style>
    /* Muted background for the plant profiles container */
    .st-key-profiles_container {
        background: rgba(127, 170, 160, 0.25);  /* muted green-blue */
        border-radius: 25px;
        padding: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def format_date_with_ordinal(d):
    day = d.day
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix} {d.strftime('%B %Y')}"

def get_all_plants():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT plant_id, name, location FROM plants ORDER BY location, name"
        ).fetchall()

def health_score(rel_rows):
    """
    Returns (score_0_to_10, due_count, total_count)
    Full bar = most plants are fine. Empty = many due/overdue.
    """
    if not rel_rows:
        return 10, 0, 0

    total = len(rel_rows)
    due_count = sum(1 for r in rel_rows if r["days_to_due"] is not None and r["days_to_due"] <= 0)

    happy = 0.0
    for r in rel_rows:
        d = r["days_to_due"]
        if d is None:
            continue
        if d > 2:
            happy += 1.0
        elif d > 0:
            happy += 0.5
        else:
            happy += 0.0

    score = int(round(10 * (happy / total)))
    return max(0, min(10, score)), due_count, total

def serious_overdue_alerts(rows, task_type, multiplier, limit=3):
    """
    Serious overdue = days_since >= multiplier * interval_days
    Excludes 'never watered/fed' (days_since is None)
    """
    candidates = []

    for r in rows:
        if r["task_type"] != task_type:
            continue

        interval_days = r["interval_days"]
        days_since = r["days_since"]

        if not interval_days or days_since is None:
            continue

        if days_since >= multiplier * interval_days:
            ratio = days_since / interval_days
            candidates.append((ratio, r))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in candidates[:limit]]

# ---------- Header ----------

st.title("My Plant Journal")

today = date.today()
season = get_season(today)

weather = get_current_weather()

nbsp = "\u00A0" # non-breaking space for better spacing in caption

if weather:
    st.caption(
    f"Today: {format_date_with_ordinal(today)}{nbsp*4}·{nbsp*4}"
    f"Season: {season.capitalize()}{nbsp*4}·{nbsp*4}"
    f"Outdoor Weather: {weather['description'].capitalize()}, {weather['temp_c']}°C, "
    f"{weather['humidity']}% humidity"
    )

else:
    st.write(f"Today: {format_date_with_ordinal(today)}  •  Season: {season.capitalize()}  •  Outdoor weather unavailable")

# ---------- Due tasks ----------
st.header("What needs doing today?")

st.space(size="small")

rows = fetch_due_tasks(today, season)  # now returns all tasks with days_to_due

water_rows = [r for r in rows if r["task_type"] == "watered"]
feed_rows  = [r for r in rows if r["task_type"] == "fed"]

w_score, w_due, w_total = health_score(water_rows)
f_score, f_due, f_total = health_score(feed_rows)

sum1, sum2 = st.columns(2)
with sum1:
    row = st.columns([1, 3, 5, 3])
    row[0].space(size="small")
    row[1].markdown("**Water status**")
    row[2].progress(w_score / 10)
    row[3].markdown(f"{w_due} due / {w_total}")  
with sum2:
    row = st.columns([1, 3, 5, 3])
    row[0].space(size="small")
    row[1].markdown("**Feeding status**")
    row[2].progress(f_score / 10)
    row[3].markdown(f"{f_due} due / {f_total}")  


# ---------- Serious overdue alerts ----------
water_alerts = serious_overdue_alerts(rows, task_type="watered", multiplier=2)
feed_alerts  = serious_overdue_alerts(rows, task_type="fed", multiplier=4)

if water_alerts or feed_alerts:
    alert_col1, alert_col2 = st.columns(2)

    with alert_col1:
        if water_alerts:
            st.warning("⚠️ Check soon - watering")
            for r in water_alerts:
                st.markdown(
                    f"- {r['name']} ({r['location']})  \n"
                    f"  Water every **{r['interval_days']}d**, last **{r['days_since']}d** ago"
                )

    with alert_col2:
        if feed_alerts:
            st.warning("⚠️ Check soon - feeding")
            for r in feed_alerts:
                st.markdown(
                    f"- {r['name']} ({r['location']})  \n"
                    f"  Feed every **{r['interval_days']}d**, last **{r['days_since']}d** ago"
                )

# Only due/overdue plants for action lists
water_due = [r for r in water_rows if r["days_to_due"] is not None and r["days_to_due"] <= 0]
feed_due  = [r for r in feed_rows  if r["days_to_due"] is not None and r["days_to_due"] <= 0]

with st.expander("**Show plants to check**", expanded=False):

    if not water_due and not feed_due:
        st.success("No watering or feeding tasks due today")
    else:
        selected_water = []
        selected_feed = []

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Consider Watering")
            if water_due:
                for r in water_due:
                    label = f"{r['name']} ({r['location']})"
                    if st.checkbox(label, key=f"water_{r['plant_id']}"):
                        selected_water.append(r)
                    st.caption(format_explanation(r, season))
            else:
                st.write("No watering due.")

        with col2:
            st.subheader("Consider Feeding")
            if feed_due:
                for r in feed_due:
                    label = f"{r['name']} ({r['location']})"
                    if st.checkbox(label, key=f"feed_{r['plant_id']}"):
                        selected_feed.append(r)
                    st.caption(format_explanation(r, season))
            else:
                st.write("No feeding due.")

        # ---------- Batch logging ----------
        st.space(size="small")

        note = st.text_input("**Log plant care with a note**",
                             placeholder="Optional note, applies to all selected plants")

        log_cols = st.columns(2)
        with log_cols[0]:
            if st.button("Log Watering", disabled=not selected_water, type="primary"):
                for r in selected_water:
                    log_event(r["plant_id"], "watered", notes=note)
                st.success(f"Logged watering for {len(selected_water)} plant(s).")
                st.rerun()

        with log_cols[1]:
            if st.button("Log Feeding", disabled=not selected_feed, type="primary"):
                for r in selected_feed:
                    log_event(r["plant_id"], "fed", notes=note)
                st.success(f"Logged feeding for {len(selected_feed)} plant(s).")
                st.rerun()

st.space(size="small")

# ---------- Log anything (not just what's due) ----------

st.subheader("Log anything (any time)")
st.caption("Use this for plant care that isn't part of the reminders - repotting, cleaning leaves, or a one-off note.")

# Pull plant list once for this section
all_plants = get_all_plants()
all_plant_ids = [p["plant_id"] for p in all_plants]
all_lookup = {p["plant_id"]: (p["name"], p["location"]) for p in all_plants}

action_labels = {
    "Watered": "watered",
    "Fed": "fed",
    "Repotted": "repotted",
    "Leaves cleaned": "leaves_cleaned",
    "Other (custom)": "other",
}

# Ensure feedback state exists
if "anytime_feedback" not in st.session_state:
    st.session_state["anytime_feedback"] = None

def submit_anytime_form():
    """Callback: log using current widget state, then clear the widgets."""
    selected_any = st.session_state.get("anytime_plants", [])
    action_choice = st.session_state.get("anytime_action", "Watered")
    event_dt = st.session_state.get("anytime_date", today)
    note_any = st.session_state.get("anytime_note", "")
    custom_action = (st.session_state.get("anytime_custom_action", "") or "").strip()

    # Decide final event_type
    if action_labels.get(action_choice) == "other":
        event_type = custom_action
    else:
        event_type = action_labels.get(action_choice, "")

    # Guard: don’t log if missing essentials
    if not selected_any or not event_type:
        st.session_state["anytime_feedback"] = ("warning", "Nothing logged — please select plant(s) and an action.")
        return

    # Log events (this is the critical part that must happen BEFORE clearing)
    for pid in selected_any:
        log_event(pid, event_type, event_date=event_dt, notes=note_any or None)

    st.session_state["anytime_feedback"] = ("success", f"Logged '{event_type}' for {len(selected_any)} plant(s).")

    # Clear inputs AFTER logging
    st.session_state["anytime_plants"] = []
    st.session_state["anytime_note"] = ""
    st.session_state["anytime_custom_action"] = ""

# Layout
log_cols = st.columns([3, 2, 2])

with log_cols[0]:
    selected_any = st.multiselect(
        "Plants",
        options=all_plant_ids,
        format_func=lambda pid: f"{all_lookup[pid][0]} ({all_lookup[pid][1]})",
        placeholder="Select one or more plants",
        key="anytime_plants",
    )

with log_cols[1]:
    action_choice = st.selectbox(
        "Action",
        options=list(action_labels.keys()),
        key="anytime_action",
    )

with log_cols[2]:
    event_dt = st.date_input(
        "Date",
        value=today,
        key="anytime_date",
        format="DD/MM/YYYY",
    )

# Custom action only when needed
if action_labels[action_choice] == "other":
    st.text_input(
        "Describe the action (used as the event type)",
        placeholder="e.g. pruned, pest check, moved location",
        key="anytime_custom_action",
    )
else:
    # Make sure stale custom_action doesn't accidentally carry over visually/mentally
    # (We still clear it on submit, but this keeps state tidy if you switch away from "Other".)
    if st.session_state.get("anytime_custom_action"):
        st.session_state["anytime_custom_action"] = ""

note_any = st.text_input(
    "Notes (optional)",
    placeholder="Anything useful to remember later",
    key="anytime_note",
)

# Decide final event_type for enabling the button (UI-only)
custom_action = (st.session_state.get("anytime_custom_action", "") or "").strip()
if action_labels[action_choice] == "other":
    event_type = custom_action
else:
    event_type = action_labels[action_choice]

can_log = bool(st.session_state.get("anytime_plants")) and bool(event_type)

# Button uses callback (no logging code inline)
st.button(
    "Log event",
    disabled=not can_log,
    type="primary",
    key="anytime_log_btn",
    on_click=submit_anytime_form,
)

# Feedback message (shows after click, persists through rerun until overwritten)
if st.session_state.get("anytime_feedback"):
    level, msg = st.session_state["anytime_feedback"]
    if level == "success":
        st.success(msg)
    else:
        st.warning(msg)

st.space(size="medium")

# ---------- Plant overview ----------
container = st.container(border=True, key="profiles_container")


with container:
    # Pull plant list once (before rendering UI that depends on it)
    plants = get_all_plants()

    left, right = st.columns([6, 1], vertical_alignment="bottom")

    with left:
        st.header("Profile & History")
        if not plants:
            st.info("No plants found in the database yet.")
            selected_plant_id = None
        else:
            plant_ids = [p["plant_id"] for p in plants]
            plant_lookup = {p["plant_id"]: (p["name"], p["location"]) for p in plants}

            selected_plant_id = st.selectbox(
                "Select a plant",
                options=plant_ids,
                format_func=lambda pid: f"{plant_lookup[pid][0]} ({plant_lookup[pid][1]})",
                key="plant_selector",
            )

    with right:
        # Always show mascot, even if no plants; keeps layout stable
        st.image("images_mascot\\drawing2.png", width=1000)

    # Everything below is full-width but still inside container
    if not plants:
        st.caption("Add a plant to start journaling.")
    elif selected_plant_id is None:
        st.caption("Select a plant to view its journal entry and history.")
    else:
        plant_id = int(selected_plant_id)

        # --- AI story (cached) ---
        @st.cache_data(show_spinner=False, ttl=60*60*12)
        def _cached_story(cache_key: tuple, api_key: str, context_bundle: dict, voice_card: str):
            return generate_plant_story(
                api_key=api_key,
                context_bundle=context_bundle,
                voice_card=voice_card,
                model_id=MODEL_ID_DEFAULT,
            )

        api_key = st.secrets["GEMINI_API_KEY"]

        context_bundle, voice_card, last_log_id = get_plant_context_bundle(
            plant_id=plant_id,
            season=season,
            today=today,
            weather=weather,
            log_limit=10,
        )

        # Botanical context line
        species = context_bundle.get("species", {})
        scientific = (species.get("scientific_name") or "").strip()
        care_context = (species.get("care_context") or "").strip()
        native_climate = (species.get("native_climate") or "").strip()

        if scientific or care_context or native_climate:
            parts = []
            if scientific:
                parts.append(f"*{scientific}*")
            if care_context:
                parts.append(f"({care_context})")
            if native_climate:
                parts.append(native_climate)
            st.write(" ".join(parts).replace(" )", ")"))

            # Cache key: uses last_log_id so it changes on every inserted care_log row
            cache_key = (plant_id, season, last_log_id, PROMPT_VERSION, MODEL_ID_DEFAULT)

            # Generate + render
            try:
                with st.spinner("Connecting to leaf notes..."):
                    story = _cached_story(cache_key, api_key, context_bundle, voice_card)

                st.subheader("Plant journal entry")  
                st.write(story.get("narrative", ""))

                highlights = story.get("highlights") or []
                if highlights:
                    st.caption("Based on:")
                    for h in highlights:
                        st.write(f"- {h}")

                suggestions = story.get("suggestions") or []
                if suggestions:
                    st.caption("What I need:")
                    for s in suggestions:
                        st.write(f"- {s}")

                unknowns = story.get("unknowns") or []
                if unknowns:
                    st.caption("Context missing:")
                    for u in unknowns:
                        st.write(f"- {u}")

            except Exception as e:
                st.error(f"AI story failed: {e}")

            # --- Small Recent care section to still print something when AI quota exceeded/AI breaks ---
            st.subheader("Recent care")
            recent = context_bundle.get("care_log_recent", [])[:5]
            if recent:
                for r in recent:
                    st.write(f"- {r.get('event_date', '')}: {r.get('event_type', '')} ({r.get('notes') or 'no notes'})")
            else:
                st.write("No care events logged yet.")

            # Raw facts / logs / schedule
            with st.expander("Details / logs / schedule"):
                st.json(context_bundle)
