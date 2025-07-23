import streamlit as st
import sqlite3
# import hashlib    # Hidden: email/password logic removed
from datetime import datetime

# --- Database Setup ---
conn = sqlite3.connect("loopbreaker.db", check_same_thread=False)
c = conn.cursor()

def init_db():
    # --- User table hidden (email/password logic removed) ---
    # c.execute("""
    #     CREATE TABLE IF NOT EXISTS users (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         email TEXT UNIQUE,
    #         password_hash TEXT,
    #         age INTEGER,
    #         gender TEXT,
    #         profession TEXT,
    #         consent INTEGER DEFAULT 0,
    #         signup_date TEXT
    #     )
    # """)
    #
    # c.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    #
    # def hash_password(pw: str) -> str:
    #     return hashlib.sha256(pw.encode()).hexdigest()

    # Progress table remains active to track user entries
    c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            question TEXT,
            response TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_progress_time ON progress(timestamp)")
    conn.commit()

init_db()

# --- Consent Form (unchanged) ---
st.subheader("📝 Informed Consent")
st.write("""
• Your responses are stored locally in this app’s database.  
• No personal data is sent to any server or third party.  
• You can delete your local data at any time by clearing the browser cache.
""")
if not st.checkbox("I have read and agree to the data policy"):
    st.warning("Consent is required to proceed.")
    st.stop()


# --- Rumination Loops & Evidence-Based Solutions ---

RUMINATION_DB = {
    "failure": {
        "prompt": "What’s one lesson you’ve taken from this so far?",
        "solution": "Cognitive restructuring: reframe setbacks as data for growth."
    },
    "stuck": {
        "prompt": "What’s the smallest step you could take now?",
        "solution": "Behavioral activation: schedule one micro-task to break inertia."
    },
    "perfection": {
        "prompt": "If you aimed for 90% instead of 100%, what would change?",
        "solution": "RFCBT: shift from abstract ‘why’ to concrete ‘how’ questions."
    },
    "guilt": {
        "prompt": "What would you tell a friend in your situation?",
        "solution": "Self-compassion: replace self-criticism with kindness."
    },
    "blame": {
        "prompt": "Which parts of this are within your control?",
        "solution": "Problem-solving therapy: separate controllables from uncontrollables."
    },
    "rejection": {
        "prompt": "Recall a time someone valued you—what did that feel like?",
        "solution": "Mindfulness: anchor in present sensations to disrupt replay."
    },
    "catastrophizing": {
        "prompt": "What’s a more realistic outcome?",
        "solution": "Decatastrophizing: test worst-case probability vs. reality."
    },
    "regret": {
        "prompt": "What can you do now to address that regret?",
        "solution": "Action planning: commit to one corrective step."
    },
    "control": {
        "prompt": "Which concern can you actually influence?",
        "solution": "ACT: accept what you can’t change, act on values you can."
    },
    "worthlessness": {
        "prompt": "Name three strengths you bring to challenges.",
        "solution": "Strength-spotting: balance neg self-views with evidence."
    },
    "comparison": {
        "prompt": "What unique resource do you have that others don’t?",
        "solution": "Gratitude practice: focus on your assets, not theirs."
    },
    "loneliness": {
        "prompt": "Who could you reach out to for brief support?",
        "solution": "Behavioral activation: schedule a 5-min connection."
    },
    "self-doubt": {
        "prompt": "What past win contradicts this doubt?",
        "solution": "Cognitive defusion: observe the thought, don’t fuse with it."
    },
    "anxiety": {
        "prompt": "What coping skill has worked before?",
        "solution": "Mindful breathing: use box-breathing to calm arousal."
    },
    "past mistakes": {
        "prompt": "What did you learn that you still use today?",
        "solution": "Journaling: extract insights, then close the chapter."
    },
    "future worry": {
        "prompt": "What’s one thing you can plan and one you can release?",
        "solution": "Worry postponement: schedule ‘worry time’ later."
    },
    "decision paralysis": {
        "prompt": "What’s the riskiest part of deciding now vs. later?",
        "solution": "Pros/cons list: time-box your decision window."
    },
    "health fears": {
        "prompt": "What preventive action can you take today?",
        "solution": "Problem-solving: focus on actionable health steps."
    },
    "financial stress": {
        "prompt": "Which cost can you adjust immediately?",
        "solution": "Behavioral budgeting: commit to one small savings goal."
    },
    "existential dread": {
        "prompt": "What value gives your life meaning right now?",
        "solution": "ACT values exercise: identify 1 value-driven action."
    },
    "identity": {
        "prompt": "Which role brings you most fulfillment?",
        "solution": "Refocused journaling: explore roles, choose one to nurture."
    },
    "change": {
        "prompt": "What’s one benefit this change might bring?",
        "solution": "Cognitive reframing: spotlight upside possibilities."
    },
    "uncertainty": {
        "prompt": "What facts do you know for sure?",
        "solution": "Reality-testing: map knowns vs. unknowns."
    },
    "commitment": {
        "prompt": "What’s a low-stakes way to test your commitment?",
        "solution": "Behavioral experiment: small trial run."
    },
    "relationship conflict": {
        "prompt": "What need lies beneath your anger?",
        "solution": "Emotion-focused therapy: name the underlying feeling."
    },
    "betrayal": {
        "prompt": "What boundary could protect you next time?",
        "solution": "Assertiveness training: define and practice boundary wording."
    },
    "trauma flashbacks": {
        "prompt": "What grounding technique can you use now?",
        "solution": "5-4-3-2-1 grounding: engage all five senses."
    },
    "childhood regrets": {
        "prompt": "What resilience skill emerged from that period?",
        "solution": "Narrative therapy: rewrite the story with growth focus."
    },
    "parenting guilt": {
        "prompt": "What’s one positive moment you shared recently?",
        "solution": "Mindful gratitude: recount simple shared joys."
    },
    "career stagnation": {
        "prompt": "What micro-skill can you learn this week?",
        "solution": "Microlearning: commit to 10 min daily practice."
    },
    "skill inadequacy": {
        "prompt": "Who could mentor you briefly on this skill?",
        "solution": "Resource activation: schedule 15 min with a peer."
    },
    "creativity block": {
        "prompt": "What random prompt could spark a new idea?",
        "solution": "Divergent thinking: try a free-write for 5 min."
    },
    "imposter syndrome": {
        "prompt": "What evidence shows you earned your role?",
        "solution": "Evidence log: list accomplishments vs. doubts."
    },
    "memory lapses": {
        "prompt": "What note-taking method helps most?",
        "solution": "External memory: set up a bullet journal."
    },
    "embarrassment": {
        "prompt": "What’s one detail you can laugh about now?",
        "solution": "Humor reappraisal: find the absurd angle."
    },
    "social anxiety": {
        "prompt": "What question could you ask someone to shift focus?",
        "solution": "Social reframing: prepare 2 open-ended questions."
    },
    "pandemic fear": {
        "prompt": "What safety measure gives you most peace?",
        "solution": "Compartmentalization: follow protocol, then shift activity."
    },
    "climate anxiety": {
        "prompt": "What one action can you take for your environment?",
        "solution": "Behavioral activation: choose a single eco-friendly habit."
    },
    "political worry": {
        "prompt": "What civic action feels meaningful to you?",
        "solution": "Values-based action: pick one letter/email task."
    },
    "moral guilt": {
        "prompt": "What restitution or apology would you offer?",
        "solution": "Restorative practice: plan and execute that step."
    },
    "envy": {
        "prompt": "What strength do you admire in yourself?",
        "solution": "Self-affirmation: write a brief strengths statement."
    },
    "jealousy": {
        "prompt": "What secure-base memory calms you?",
        "solution": "Secure attachment imagery: recall supportive moments."
    },
    "aging fears": {
        "prompt": "What wisdom has come with your years?",
        "solution": "Life review: journal one pride moment per decade."
    },
    "mortality": {
        "prompt": "What bucket-list item could you plan now?",
        "solution": "Goal-setting: choose one item and outline steps."
    },
    "time passing": {
        "prompt": "What daily ritual brings you joy?",
        "solution": "Mindful ritual: integrate joy practice each morning."
    },
    "academic anxiety": {
        "prompt": "What study slice can you complete in 10 min?",
        "solution": "Pomodoro: commit to one focused interval."
    },
    "peer pressure": {
        "prompt": "What value guides your choices here?",
        "solution": "Values clarification: list top 3, align actions."
    },
    "need to be liked": {
        "prompt": "What would you say if you weren’t seeking approval?",
        "solution": "Assertive scripting: craft and practice that statement."
    },
    "what-if thinking": {
        "prompt": "Which outcomes are realistic vs. fantasy?",
        "solution": "Probability mapping: assign 0–100% likelihood."
    },
    "negative self-talk": {
        "prompt": "What’s a kinder phrase you could use instead?",
        "solution": "Self-compassion dialogue: script alternative."
    },
    "worry about loved ones": {
        "prompt": "What support can you offer them today?",
        "solution": "Behavioral activation: schedule check-in call."
    },
    "caregiver burden": {
        "prompt": "What moment of rest can you plan now?",
        "solution": "Self-care prescription: block 15 min of downtime."
    }

    # …you can extend this dictionary with additional loops.
}

# --- Authentication ---

def signup():
    st.subheader("🔐 Sign Up")
    email = st.text_input("Email", key="su_email")
    pw = st.text_input("Password", type="password", key="su_pw")
    if st.button("Create Account"):
        pw_hash = hash_password(pw)
        try:
            c.execute("""
                INSERT INTO users (email, password_hash, signup_date)
                VALUES (?, ?, ?)
            """, (email, pw_hash, datetime.utcnow().isoformat()))
            conn.commit()
            st.success("Account created! Please log in.")
        except sqlite3.IntegrityError:
            st.error("That email is already registered.")

def login():
    st.subheader("🔑 Log In")
    email = st.text_input("Email", key="li_email")
    pw = st.text_input("Password", type="password", key="li_pw")
    if st.button("Log In"):
        pw_hash = hash_password(pw)
        c.execute("""
            SELECT id, email, age, gender, profession, consent, signup_date
            FROM users WHERE email=? AND password_hash=?
        """, (email, pw_hash))
        row = c.fetchone()
        if row:
            st.session_state.user = {
                "id": row[0],
                "email": row[1],
                "age": row[2],
                "gender": row[3],
                "profession": row[4],
                "consent": row[5],
                "signup_date": datetime.fromisoformat(row[6])
            }
            st.success("Logged in!")
        else:
            st.error("Invalid credentials.")

# --- Demographics & Consent ---

def collect_demographics(user):
    st.subheader("👤 Tell us about you")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Prefer not to say","Female","Male","Other"])
    profession = st.text_input("Profession / Student status")
    if st.button("Save Demographics"):
        if age < 18:
            st.warning("This app is for 18+ only. Come back when you’re older.")
            st.stop()
        c.execute("""
            UPDATE users SET age=?, gender=?, profession=? WHERE id=?
        """, (age, gender, profession, user["id"]))
        conn.commit()
        st.experimental_rerun()

def ask_consent(user):
    st.subheader("📝 Informed Consent")
    st.write("""
        • Your data is stored securely and privately.  
        • No sharing with third parties.  
        • You may request deletion at any time via loopbreakerMD@gmail.com  
    """)
    if st.checkbox("I agree to the data policy"):
        c.execute("UPDATE users SET consent=1 WHERE id=?", (user["id"],))
        conn.commit()
        st.experimental_rerun()
    else:
        st.warning("Consent is required to proceed.")
        st.stop()

# --- Unwinding Logic ---

def unwind_session(user):
    if "depth" not in st.session_state:
        st.session_state.depth = 0
        st.session_state.question = st.session_state.start_question

    if st.session_state.depth >= 3:
        st.info("↪️  Loop limit reached. Try journaling or talking it out.")
        return

    indent = "    " * st.session_state.depth
    st.write(f"{indent}🤔 {st.session_state.question}")
    response = st.text_input("Your thoughts here:", key=f"resp_{st.session_state.depth}")

    if st.button("Next", key=f"btn_{st.session_state.depth}"):
        # Log progress
        c.execute("""
            INSERT INTO progress (user_id, timestamp, question, response)
            VALUES (?, ?, ?, ?)
        """, (user["id"], datetime.utcnow().isoformat(),
              st.session_state.question, response))
        conn.commit()

        # Check for rumination keywords
        low = response.lower()
        for kw, data in RUMINATION_DB.items():
            if kw in low:
                st.warning(f"{indent}🔁 You seem to be circling: '{kw}'")
                st.success(f"{indent}💡 {data['prompt']}")
                st.write(f"{indent}📖 {data['solution']}")
                return

        # Recurse deeper
        st.session_state.depth += 1
        st.session_state.question = response
        st.experimental_rerun()

# --- Main App ---

st.title("LoopBreakerMD: Decision Loop Unwinder")
if "user" not in st.session_state:
    st.write("For help, visit [docs.streamlit.io](https://docs.streamlit.io/).")
    mode = st.radio("Have an account?", ["Log In","Sign Up"])
    if mode == "Sign Up":
        signup()
    else:
        login()
    st.stop()

user = st.session_state.user

# Demographics
if user["age"] is None:
    collect_demographics(user)

# Consent
if not user["consent"]:
    ask_consent(user)

# Unwinding interface
st.header("🌀 Explore Your Thought Loop")
question = st.text_input(
    "Enter a decision or situation you’re overthinking:",
    key="start_q"
)
if st.button("Start Unwinding"):
    if question.strip():
        st.session_state.start_question = question
        unwind_session(user)
    else:
        st.error("Please enter something to explore.")

# 7-day & 14-day reminders
delta = datetime.utcnow() - user["signup_date"]
if delta.days == 7:
    st.info("📅 Day 7 Check-in: Review your past entries and notice patterns.")
elif delta.days == 14:
    st.success("🎉 14-Day Milestone! Celebrate your insights and plan next steps.")

st.markdown("---")
st.markdown("""
## Proudly powered by loopbreakerMD  
Need expert guidance? Reach us at [loopbreakerMD@gmail.com](mailto:loopbreakerMD@gmail.com)
""")
