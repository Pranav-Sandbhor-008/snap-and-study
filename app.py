import json

import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
    IMAGE_EXPLANATION_PROMPT,
    EXAM_PREP_PROMPT,
)


# =========================================================
# 1. Page Configuration
# =========================================================

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚"
)


# =========================================================
# 2. API Keys and Secrets
# =========================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]

TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]

TWILIO_WHATSAPP_FROM = st.secrets["TWILIO_WHATSAPP_FROM"]

TWILIO_CONTENT_SID = st.secrets["TWILIO_CONTENT_SID"]


# =========================================================
# 3. Model Configuration
# =========================================================

MODEL_NAME = "gemini-3.8-flash"


# =========================================================
# 4. Gemini Client
# =========================================================

@st.cache_resource
def get_gemini_client():

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# 5. Twilio Client
# =========================================================

@st.cache_resource
def get_twilio_client():

    return TwilioClient(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN
    )


gemini_client = get_gemini_client()

twilio_client = get_twilio_client()


# =========================================================
# 6. Initialize Session State
# =========================================================

if "onboarded" not in st.session_state:

    st.session_state.onboarded = False


if "name" not in st.session_state:

    st.session_state.name = ""


if "whatsapp_number" not in st.session_state:

    st.session_state.whatsapp_number = ""


if "messages" not in st.session_state:

    st.session_state.messages = []


if "chat" not in st.session_state:

    st.session_state.chat = None


# =========================================================
# 7. Render Chat Messages
# =========================================================

def render_message(message):

    with st.chat_message(message["role"]):

        if message["kind"] == "text":

            st.write(message["content"])

        elif message["kind"] == "image":

            st.image(message["content"])


# =========================================================
# 8. Add Chat Message
# =========================================================

def add_message(role, kind, content):

    message = {
        "role": role,
        "kind": kind,
        "content": content
    }

    st.session_state.messages.append(message)

    render_message(message)


# =========================================================
# 9. Ask Gemini
# =========================================================

def ask_gemini(parts):

    try:

        response = st.session_state.chat.send_message(
            parts
        )

        return response.text

    except Exception as error:

        return (
            f"Sorry, something went wrong while "
            f"processing your question: {error}"
        )


# =========================================================
# 10. Clean WhatsApp Message
# =========================================================

def clean_whatsapp_text(text):

    if not text:

        return "No study summary available."

    text = " ".join(text.split())

    return (
        text[:1500] + "..."
        if len(text) > 1500
        else text
    )


# =========================================================
# 11. Send Study Summary to WhatsApp
# =========================================================

def send_whatsapp(to_number, user_name, summary):

    # Twilio Content Template:
    # {{1}} = student name
    # {{2}} = study summary

    try:

        content_variables = json.dumps(
            {
                "1": user_name,
                "2": clean_whatsapp_text(summary)
            },
            ensure_ascii=False
        )

        message = twilio_client.messages.create(

            from_=TWILIO_WHATSAPP_FROM,

            to=f"whatsapp:{to_number}",

            content_sid=TWILIO_CONTENT_SID,

            content_variables=content_variables,
        )

        return True, message.sid

    except Exception as error:

        return False, str(error)


# =========================================================
# 12. Onboarding
# =========================================================

if not st.session_state.onboarded:

    st.title("👋 I'm Snap & Study 📚")

    st.caption(
        "📸 Snap a problem, understand the concept, "
        "and study smarter with AI. 🤖"
    )

    with st.form("onboarding_form"):

        name = st.text_input(
            "Your name"
        )

        whatsapp_number = st.text_input(
            "WhatsApp number (with country code)",
            placeholder="+91XXXXXXXXXX",
            help="Your study summary will be sent to this number."
        )

        submitted = st.form_submit_button(
            "Let's study 🚀"
        )


    if submitted:

        if (
            not name.strip()
            or not whatsapp_number.strip()
        ):

            st.warning(
                "Please fill in both your name "
                "and WhatsApp number."
            )

        else:

            st.session_state.name = name.strip()

            st.session_state.whatsapp_number = (
                whatsapp_number.strip()
            )


            # Create Gemini conversation

            st.session_state.chat = (
                gemini_client.chats.create(

                    model=MODEL_NAME,

                    config=types.GenerateContentConfig(

                        system_instruction=SYSTEM_PROMPT

                    ),
                )
            )


            st.session_state.messages = []

            st.session_state.onboarded = True

            st.rerun()


    st.stop()


# =========================================================
# 13. Snap & Study Header
# =========================================================

header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)


with header_col:

    st.title("📚 Snap & Study")


with button_col:

    send_disabled = (
        len(st.session_state.messages) <= 1
    )


    if st.button(
        "📤 Send to WhatsApp",
        disabled=send_disabled,
        use_container_width=True
    ):

        with st.spinner(
            "Preparing your study summary..."
        ):

            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )


        success, info = send_whatsapp(

            st.session_state.whatsapp_number,

            st.session_state.name,

            summary

        )


        if success:

            st.success(
                "Study summary sent! 📲"
            )

        else:

            st.error(
                f"Couldn't send that: {info}"
            )


# =========================================================
# 14. User Information
# =========================================================

st.caption(

    f"Logged in as {st.session_state.name} - "

    f"updates go to "
    f"{st.session_state.whatsapp_number}"

)


# =========================================================
# 15. Display Chat History
# =========================================================

if not st.session_state.messages:

    add_message(

        "assistant",

        "text",

        WELCOME_MESSAGE_TEMPLATE.format(

            name=st.session_state.name

        )

    )

else:

    for message in st.session_state.messages:

        render_message(message)


# =========================================================
# 16. Chat Input
# =========================================================

user_input = st.chat_input(

    "Ask a study question, or attach a problem/diagram",

    accept_file=True,

    file_type=[
        "jpg",
        "jpeg",
        "png"
    ]

)


# =========================================================
# 17. Process User Input
# =========================================================

if user_input:

    photo = (

        user_input.files[0]

        if user_input.files

        else None

    )

    text = user_input.text

    parts = []


    # -----------------------------------------------------
    # Uploaded Image
    # -----------------------------------------------------

    if photo is not None:

        photo_bytes = photo.getvalue()


        add_message(

            "user",

            "image",

            photo_bytes

        )


        parts.append(

            types.Part.from_bytes(

                data=photo_bytes,

                mime_type=photo.type

            )

        )


    # -----------------------------------------------------
    # Text Question
    # -----------------------------------------------------

    if text:

        add_message(

            "user",

            "text",

            text

        )


        parts.append(text)


    # -----------------------------------------------------
    # Image Only
    # -----------------------------------------------------

    elif photo is not None:

        parts.append(

            IMAGE_EXPLANATION_PROMPT

        )


    # -----------------------------------------------------
    # Send to Gemini
    # -----------------------------------------------------

    if parts:

        with st.spinner(

            "Understanding your question..."

        ):

            answer = ask_gemini(parts)


        # -------------------------------------------------
        # Display Gemini Answer
        # -------------------------------------------------

        add_message(

            "assistant",

            "text",

            answer

        )