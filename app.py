import google.generativeai as genai
from PIL import Image
import streamlit as st
import time

# Directly configure API Key
genai.configure(api_key="AIzaSyBpmJh4SGPYgmkbObdYKmQLwWz8TizsKaM")

# Function to load Google Gemini Vision Model and get response
def get_response_image(image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([image[0], prompt])
    return response.text

# Function to load Google Gemini Pro Model and get response
def get_response(prompt, input_text):
    model = genai.GenerativeModel('gemini-1.5-flash-8b-exp-0924')
    try:
        response = model.generate_content([prompt, input_text])
        if not response.text or len(response.text.strip()) < 10:  # Check for minimal meaningful response
            return "Error: Incomplete response from the model. Please try again or check your input."
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Function to prepare Image Data
def prep_image(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No File is uploaded!")

# Function to simulate typing effect with controlled font size
def type_response(response, placeholder):
    full_response = ""
    for chunk in response.split():
        full_response += chunk + " "
        time.sleep(0.05)  # Adjust the speed of typing here
        placeholder.markdown(f'<div class="typing-message">{full_response}▌</div>', unsafe_allow_html=True)
    placeholder.markdown(f'<div class="chat-message bot-message">{full_response}</div>', unsafe_allow_html=True)
    return

# Initialize the Streamlit app
st.set_page_config(page_title="Planner: Discover and Plan your Culinary Adventures!", layout="wide")
st.image('logo.jpg', width=70)
st.markdown("<h1 style='text-align: center; color: white;'>Planner: Discover and Plan your Culinary Adventures!</h1>", unsafe_allow_html=True)

# Custom CSS to enhance the UI and match the photo style, with typing font control
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextArea>textarea {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 10px;
        background-color: #f0f0f0;
    }
    .stRadio>div {
        flex-direction: row;
        display: flex;
        gap: 10px;
        background-color: #1a1a1a;
        padding: 10px;
        border-radius: 5px;
    }
    .stRadio>div>label {
        margin-bottom: 0;
        color: white;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 70%;
        background-color: #f5f5f5;
        color: #333;
        font-size: 16px; /* Ensure consistent final font size */
    }
    .user-message {
        margin-left: auto;
        background-color: #e1f5fe;
    }
    .bot-message {
        margin-right: auto;
    }
    .typing-message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 70%;
        background-color: #f5f5f5;
        color: #333;
        font-size: 16px; /* Control typing font size */
    }
    body {
        background-color: #1a1a1a;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Creating radio section choices
section_choice = st.radio("Choose Section:", 
                          ("Location Finder", "Trip Planner", "Weather Forecasting", "Restaurant & Hotel Planner"))

# Session state to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Placeholder for chat history
chat_placeholder = st.empty()

###########################################################################################
# If the choice is Location Finder
if section_choice == "Location Finder":
    st.subheader("Location Finder")
    upload_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if upload_file is not None:
        image = Image.open(upload_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    input_prompt_loc = """
    You are an expert Tourist Guide. As an expert, your job is to provide a summary about the place and:
    - Location of the place
    - State & Capital
    - Coordinates of the place
    - Some popular places nearby
    Return the response using markdown.
    """

    submit = st.button("Get Location!")
    if submit and upload_file is not None:
        try:
            image_data = prep_image(upload_file)
            response = get_response_image(image_data, input_prompt_loc)
            st.session_state.chat_history.append({"role": "user", "content": "Get location from image"})
            st.session_state.chat_history.append({"role": "bot", "content": response})
            type_response(response, chat_placeholder)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

###########################################################################################
# If the choice is Trip Planner
if section_choice == "Trip Planner":
    st.subheader("Trip Planner")
    input_prompt_planner = """
    You are an expert Tour Planner. Your job is to provide recommendations and plan for a given location for a given number of days,
    even if the number of days is not provided.
    Also, suggest hidden secrets, hotels, and beautiful places we shouldn't forget to visit.
    Also, tell the best month to visit the given place.
    Return the response using markdown.
    """

    input_plan = st.text_area("Provide location and number of days to obtain an itinerary plan! (e.g., '3 days for Ranchi')", value="3 days for ranchi")
    submit1 = st.button("Plan my Trip!")
    if submit1 and input_plan.strip():
        try:
            parts = input_plan.lower().split("for")
            if len(parts) != 2:
                st.error("Please provide input in the format: 'X days for Location' (e.g., '3 days for Ranchi').")
            else:
                days = parts[0].strip().split()[0]
                location = parts[1].strip()
                response = get_response(input_prompt_planner, f"{days} days trip plan for {location.capitalize()}")
                st.session_state.chat_history.append({"role": "user", "content": input_plan})
                st.session_state.chat_history.append({"role": "bot", "content": response})
                chat_placeholder.empty()  # Clear previous content
                type_response(response, chat_placeholder)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

###########################################################################################
# If the choice is Weather Forecasting
if section_choice == "Weather Forecasting":
    st.subheader("Weather Forecasting")
    input_prompt_weather = """
    You are an expert weather forecaster. Your job is to provide a forecast for a given place for the next 7 days,
    including:
    - Precipitation
    - Humidity
    - Wind
    - Air Quality
    - Cloud Cover
    Return the response using markdown.
    """
    input_plan = st.text_area("Provide location to forecast weather!")
    submit2 = st.button("Forecast Weather!")
    if submit2 and input_plan.strip():
        try:
            response = get_response(input_prompt_weather, input_plan)
            st.session_state.chat_history.append({"role": "user", "content": input_plan})
            st.session_state.chat_history.append({"role": "bot", "content": response})
            type_response(response, chat_placeholder)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

###########################################################################################
# If the choice is Restaurant & Hotel Planner
if section_choice == "Restaurant & Hotel Planner":
    st.subheader("Restaurant & Hotel Planner")
    input_prompt_restaurant = """
    You are an expert Restaurant & Hotel Planner. 
    Your job is to provide Restaurant & Hotel recommendations for a given place that are not very expensive or very cheap.
    - Provide the rating of the restaurant/hotel
    - Top 5 restaurants with address and average cost per cuisine
    - Top 5 hotels with address and average cost per night
    Return the response using markdown.
    """
    input_plan = st.text_area("Provide location to find Hotels & Restaurants!")
    submit3 = st.button("Find Restaurant & Hotel!")
    if submit3 and input_plan.strip():
        try:
            response = get_response(input_prompt_restaurant, input_plan)
            st.session_state.chat_history.append({"role": "user", "content": input_plan})
            st.session_state.chat_history.append({"role": "bot", "content": response})
            type_response(response, chat_placeholder)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display Chat History
with chat_placeholder.container():
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message">{message["content"]}</div>', unsafe_allow_html=True)
