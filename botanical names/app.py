import streamlit as st
import pandas as pd
import random
import os

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Flash Card Vilaiyattu", layout="wide")
CARD_FRONT = "botanical names/images/card_front.png"
CARD_BACK = "botanical names/images/card_back.png"
WORDS_TO_LEARN_CSV = "botanical names/words_to_learn.csv"
CSV_FILE = "botanical names/my_flashcards.csv"

# -------------------- LOAD DATA --------------------
def load_words():
    """Load words safely — fallback to my_flashcards.csv if words_to_learn.csv is missing or empty."""
    if os.path.exists(WORDS_TO_LEARN_CSV):
        try:
            df = pd.read_csv(WORDS_TO_LEARN_CSV)
            if df.empty or not {"Question", "Answer"}.issubset(df.columns):
                raise ValueError("Empty or invalid CSV")
            return df
        except Exception:
            pass  # fall back to main CSV

    # fallback
    df = pd.read_csv(CSV_FILE)
    return df

# Load or show error
try:
    df = load_words()
except FileNotFoundError:
    st.error(f"Could not find '{CSV_FILE}'. Make sure it's in the same folder as this app.")
    st.stop()

if not {"Question", "Answer"}.issubset(df.columns):
    st.error("CSV must contain columns named exactly 'Question' and 'Answer'.")
    st.stop()

all_words = df.to_dict(orient="records")

# -------------------- SESSION STATE --------------------
if "remaining" not in st.session_state:
    st.session_state.remaining = all_words.copy()
if "current" not in st.session_state:
    st.session_state.current = random.choice(st.session_state.remaining) if st.session_state.remaining else None
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# -------------------- FUNCTIONS --------------------
def pick_new_word():
    if st.session_state.remaining:
        st.session_state.current = random.choice(st.session_state.remaining)
    else:
        st.session_state.current = None
    st.session_state.show_answer = False

def btn_show_answer():
    st.session_state.show_answer = True

def btn_skip():
    pick_new_word()

def btn_i_knew_it():
    cur = st.session_state.current
    if cur in st.session_state.remaining:
        st.session_state.remaining.remove(cur)
        pd.DataFrame(st.session_state.remaining).to_csv(WORDS_TO_LEARN_CSV, index=False)
    pick_new_word()

def btn_restart():
    if os.path.exists(WORDS_TO_LEARN_CSV):
        os.remove(WORDS_TO_LEARN_CSV)
    st.session_state.remaining = all_words.copy()
    pick_new_word()

# -------------------- HEADER --------------------
st.markdown(
    """
    <div style="text-align:center;padding:8px;">
        <h1 style="margin:6px;font-size:30px;">Flash Card Vilaiyattu</h1>
        <div style="color:#444;font-size:18px;">Botanical names</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- GAME OVER --------------------
if st.session_state.current is None:
    st.markdown(
        "<div style='text-align:center;margin-top:60px;'>"
        "<h2 style='font-size:56px;color:green'>🎉 Game Over! You knew all the words! 🎉</h2>"
        "<p style='font-size:20px'>Press the button below to restart the game.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.button("🔄 Restart Game", on_click=btn_restart, use_container_width=True)
    st.stop()

# -------------------- CARD DISPLAY --------------------
# -------------------- CARD DISPLAY --------------------
cur = st.session_state.current
front_text = cur["Question"]
back_text = cur["Answer"]

# Dynamically swap image & text
if st.session_state.show_answer:
    card_image = CARD_BACK
    card_text = back_text
    font_style = "italic"
else:
    card_image = CARD_FRONT
    card_text = front_text
    font_style = "normal"

# Use base64 to force reload image
import base64
from pathlib import Path

def img_to_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_b64 = img_to_base64(card_image)

card_html = f"""
<style>
.card {{
  width: 90%;
  max-width: 1100px;
  height: 640px;
  margin: 24px auto;
  position: relative;
  border-radius: 20px;
  box-shadow: 0px 12px 30px rgba(0,0,0,0.25);
  background: url('data:image/png;base64,{bg_b64}') center/cover no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.card-text {{
  padding: 30px;
  text-align: center;
  font-weight: 700;
  font-style: {font_style};
  line-height: 1.05;
  font-size: clamp(40px, 8vw, 160px);
  color: black;
  word-break: break-word;
  max-width: 88%;
}}
</style>

<div class="card">
  <div class="card-text">{card_text}</div>
</div>
"""
st.markdown(card_html, unsafe_allow_html=True)


# -------------------- BUTTONS --------------------
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.button("⏭ Skip", on_click=btn_skip, use_container_width=True)
with c2:
    st.button("👁 Show Answer", on_click=btn_show_answer, use_container_width=True)
with c3:
    st.button("✅ I Knew It", on_click=btn_i_knew_it, use_container_width=True)


