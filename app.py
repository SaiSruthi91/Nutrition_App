# Import libraries
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import streamlit as st

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to analyze image and return identified food items with their nutritional information
def get_response_nutrition(image, prompt):
    # Configure the generative model for image processing
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Send the image data separately for analysis
    response = model.generate_content({
        "parts": [
            {
                "mime_type": image["mime_type"],
                "data": image["bytes"]
            }
        ]
    })
    
    # Get identified food items
    food_identification = response.text  # This would contain identified food items
    
    # Now, create a follow-up prompt to ask for nutritional details based on identified food items
    nutrition_prompt = f"""
    For the following food items, provide detailed nutritional information including:
    - Calories
    - Protein (g)
    - Fat (g)
    - Carbs (g)
    - Fiber (g)
    - Key Vitamins & Minerals

    Here are the identified food items:
    {food_identification}
    """

    # Get detailed nutritional analysis
    nutrition_response = model.generate_content(nutrition_prompt)
    return nutrition_response.text  # Return the detailed nutritional information

# Function to load Google Gemini Pro model and get diet response
def get_response_diet(prompt, input):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([prompt, input])
    return response.text

# Preprocess image data
def prep_image(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = {
            "mime_type": uploaded_file.type,
            "bytes": bytes_data
        }
        return image_parts
    else:
        raise FileNotFoundError("No File is uploaded!")

# Streamlit App Configuration

st.set_page_config(page_title="Health Management: Nutrition Calculator & Diet Planner")
st.header("Health: Nutrition Calculator & Diet Planner")

# Section selector
section_choice = st.radio("Choose Section:", ("Nutrition Calculator", "Diet Planner"))

if section_choice == "Nutrition Calculator":
    upload_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if upload_file is not None:
        image = Image.open(upload_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
    
    input_prompt_nutrition = """
    You are an expert Nutritionist. Analyze the food items in the image and identify each item. 
    Provide a summary of each food item.
    """
    
    submit = st.button("Identify Food and Get Nutrition Value!")

    if submit:
        image_data = prep_image(upload_file)
        response = get_response_nutrition(image_data, input_prompt_nutrition)
        
        st.subheader("Nutrition AI: ")
        
        # Display the response with identified food items and their nutritional breakdown
        st.markdown(f"""
        ### Identified Food Items and Nutritional Breakdown:
        {response}
        """)

if section_choice == "Diet Planner":
    input_prompt_diet = """
    You are an expert Nutritionist. If the input contains a list of items like fruits or vegetables, 
    create a diet plan and suggest breakfast, lunch, and dinner. 
    If the input contains a number, suggest a diet plan for the whole day within the given calorie limit.
    Return the response in markdown format.
    """
    input_diet = st.text_area("Input the list of items that you have at home or specify how many calories you want to consume per day:")
    submit1 = st.button("Plan my Diet!")

    if submit1:
        response = get_response_diet(input_prompt_diet, input_diet)
        st.subheader("Diet AI: ")
        st.write(response)