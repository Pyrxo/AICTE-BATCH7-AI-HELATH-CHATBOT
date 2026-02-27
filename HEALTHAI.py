import os
import google.generativeai as genai
from PIL import Image
import streamlit as st

# Check if running in Google Colab environment
if 'google.colab' in sys.modules:
    from google.colab import userdata
    GOOGLE_API_KEY=userdata.get('Gemini_API_Key')
else:
    # If not in Colab, try to get the API key from environment variables
    GOOGLE_API_KEY=os.getenv('Gemini_API_Key')
    if GOOGLE_API_KEY is None:
        # Raise an error if the API key is not found in environment variables outside Colab
        raise ValueError("Gemini_API_Key not found in environment variables. Please set the 'Gemini_API_Key' environment variable or run in a Colab environment with the key set in UserData.")

genai.configure(api_key=GOOGLE_API_KEY)

if'health_profile' not in st.session_state:
    st.session_state.health_profile ={
        'goals': 'lose 10 pounds in 3 months\nImprove cardiovascular health',
        'conditions': 'none',
        'routines' : '30-minute walk 3x/week',
        'restrictions': 'vegetarian\nLow carb',
        'preferences': '', # Added for consistency
        'daily_calorie_goal': 2000, # Initializing daily_calorie_goal
    }

# Initialize daily_food_log if it doesn't exist
if 'daily_food_log' not in st.session_state:
    st.session_state.daily_food_log = []

def get_gemini_response(input_prompt,image_data=None):
    model =genai.GenerativeModel('gemini-2.5-flash')

    content =[input_prompt]

    if image_data:
        content.extend(image_data)

    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating response:{str(e)}"
def input_image_setup( uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts =[{
            "mime_type": uploaded_file.type,
            "data":bytes_data
        }]
        return image_parts
    return None

st.set_page_config(page_title="AI Health Companion",layout="wide")
st.header("AI Health Companion")

with st.sidebar:
    st.subheader("Your Health Profile")

    health_goals =st.text_area("Health Goals",
                             value=st.session_state.health_profile['goals'])
    medical_conditions =st.text_area("Medical Conditions",
                                    value=st.session_state.health_profile['conditions'])
    fitness_routines =st.text_area("Fitness Routines",
                                    value=st.session_state.health_profile.get('routines', '')) # Using .get() for robustness
    food_preferences =st.text_area("Food Preferences",
                                    value=st.session_state.health_profile.get('preferences', '')) # Using .get() for robustness
    restrictions =st.text_area("Dietary Restrictions",
                                    value=st.session_state.health_profile['restrictions'])

    # Add a st.number_input for 'Daily Calorie Goal'
    daily_calorie_goal = st.number_input("Daily Calorie Goal",
                                        min_value=1000,
                                        max_value=5000,
                                        value=st.session_state.health_profile.get('daily_calorie_goal', 2000)) # Default to 2000 if not found

    if st.button("Update Profile"):
        st.session_state.health_profile ={
        'goals': health_goals,
        'conditions': medical_conditions,
        'routines' : fitness_routines,
        'preferences': food_preferences, # Corrected key from 'prefrences'
        'restrictions': restrictions,
        'daily_calorie_goal': daily_calorie_goal, # Save the new input
        }
        st.success("Profile updated!")

# Walkthrough content embedded here, outside of tabs, using st.expander
with st.expander("## **✨ App Features Walkthrough ✨**"):
    st.markdown("### **Your Health Profile (Sidebar)**")
    st.info("**Purpose**: This section, always visible on the left sidebar, allows you to personalize your health and dietary information.\n**How to Use**: Fill in your Health Goals, Medical Conditions, Fitness Routines, Food Preferences, Dietary Restrictions, and Daily Calorie Goal. Click the Update Profile button to save your changes. This information is crucial for generating personalized recommendations in other sections.")

    st.markdown("### **Meal Planning (Tab 1)**")
    st.info("**Purpose**: Get personalized 7-day meal plans based on your health profile.\n**How to Use**:\n1. Ensure your Health Profile in the sidebar is up-to-date.\n2. Optionally, add any specific requirements (e.g., 'quick meals for work') in the Your Current Needs text area.\n3. Click the Generate Personalized Meal Plan button.\n4. The AI will generate a detailed meal plan including nutritional breakdown, contextual explanations, a shopping list, and preparation tips.\n5. You can Download Meal Plan as a text file.")

    st.markdown("### **Food Analysis (Tab 2)**")
    st.info("**Purpose**: Analyze the nutritional content of your food from an image.\n**How to Use**:\n1. Click Browse files to upload an image of your food (e.g., a plate of a meal).\n2. Once the image is displayed, click the Analyze Food button.\n3. The AI will provide estimated calories, macronutrient breakdown, health benefits, concerns based on restrictions, and suggested portion sizes.")

    st.markdown("### **Health Insights (Tab 3)**")
    st.info("**Purpose**: Ask any health or nutrition-related questions and get expert, science-backed insights.\n**How to Use**:\n1. Type your question (e.g., 'how can I improve my gut health?') in the input field.\n2. Click Get Expert Insights.\n3. The AI will provide detailed explanations, practical recommendations, precautions, and references, considering your health profile.")

    st.markdown("### **Daily Calorie Tracker (Tab 4)**")
    st.info("**Purpose**: Log your food intake and track your daily calorie consumption against your set goal.\n**How to Use**:\n1. In the input fields, enter a Food Item and its Calories (you can use Food Analysis to estimate calories).\n2. Click Add Food to add it to your daily log.\n3. The tracker will display your Consumed / Goal calories, a progress bar showing your percentage of the daily goal, and messages indicating if you are under, met, or exceeded your goal.\n4. Click Reset Daily Log to clear all entries and start fresh for the day.")

    st.markdown("### **Yoga (Tab 5)**")
    st.info("**Purpose**: Get insights and instructions on various yoga poses and their benefits.\n**How to Use**:\n1. Type your yoga-related question (e.g., 'What are the benefits of Downward Dog pose?') in the input field.\n2. Click Get Yoga Insights.\n3. The AI will provide explanations, step-by-step instructions, physical and mental benefits, precautions, and who might benefit most from the pose.")

tab1, tab2, tab3, tab4, tab5 =st.tabs(["Meal Planning","Food Analysis","Health Insights", "Calorie Tracker", "Yoga"])

with tab1:
    st.subheader("Personalized Meal Planning")

    col1,col2 =st.columns(2)

    with col1:
         st.write("###Your Current Needs ")
         user_inputs =st.text_area("Describe any specific requirements for your meal plan",
                                 placeholder="e.g., 'I  need quick meals for work place'")
    with col2:
        st.write("###Your Health Profile")
        st.json(st.session_state.health_profile)

    if st.button("Generate Personalised Meal Plan"):
        if not any(st.session_state.health_profile.values()):
            st.warning("please complete your health pprofile in the  sidebar")

        else:
            with st.spinner("creating your personalised meal plan..."):
                prompt =f"""
                Create a personalised meal plan based on the following health factors:
                Goals: {st.session_state.health_profile['goals']}
                Conditions: {st.session_state.health_profile['conditions']}
                Routines: {st.session_state.health_profile['routines']}
                Restrictions: {st.session_state.health_profile['restrictions']}
                Preferences: {st.session_state.health_profile['preferences']}
                Daily Calorie Goal: {st.session_state.health_profile['daily_calorie_goal']} Calories
                User specific requirements: {user_inputs if user_inputs else 'None'}

                 Provide:
                 1. A 7 day meal plan with breakfast, lunch,dinner,and snacks
                 2. Nutritionaln breakdown for each day (calories,  macros)
                 3.Contextual ecplainations  for why eachmeal wwas chosen
                 4.Shopping list organised by category
                 5.Preparations tips and time saving suggestions
                 Format the outputs clearly  with headings and bullet points.
                """

                response= get_gemini_response(prompt)
                st.subheader("your personalised meal plan")
                st.markdown(response)

                st.download_button(
                 label="Download Meal Plan",
                 data=response,
                 file_name="personalised_meal_plan.txt",
                 mime="text/plain"
                )
with tab2:
  st.subheader("food anlysis")

  uploaded_file=st.file_uploader("upload an image of your food",
                                 type=["jpg","jpeg","png"])
  if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image,caption="uploaded food image.",use_column_width=True)
  if st.button("analyze food"):
    with st.spinner("analyzing your food..."):
      image_data =input_image_setup(uploaded_file)

      prompt=f"""
      you are an expert  nutrionist analyze this food image.
      provide detailed  information about:
      -estimmated calories
      -macronutrient breakdown
      -potential  health benefits
      -any concerns based on common dietary restrictions
      -suggested portion sizes
      if the food contains multiple items analyze each separately.
      """
      response =get_gemini_response(prompt,image_data)
      st.subheader("food anlysis results")
      st.markdown(response)
with tab3:
   st.subheader("health insights")
   health_query=st.text_input("ask any health/nutrition related question",
   placeholder='e.g.,\'how can i improve my gut health')
   if st.button("get expert insights"):
       if not health_query:
          st.warning("Please enter a health question")
       else:
           with st.spinner("reserching your question..."):
             prompt=f"""
             you are a certified nutrionist and health expert.
             provide detailed ,science backed insights about:
             {health_query}
             consider the user's health profiles:
             {st.session_state.health_profile}
             include:
             1. clear explanations of the science
             2.practical recommeddations
             3.any relevant precautions
             4.refrences to studies
             use simple language but maintain accuracy.
             """
             response=get_gemini_response(prompt)
             st.subheader("expert helath insights")
             st.markdown(response)

with tab4:
    st.subheader("Daily Calorie Tracker")

    food_item = st.text_input("Food Item")
    calories_input = st.text_input("Calories", placeholder="ENTER THE CALORIE OF YOUR ITEM YOU WILL FIND THROUGH FOOD ANALYSIS")
    calories = 0
    if calories_input:
        try:
            calories = int(calories_input)
        except ValueError:
            st.error("Please enter a valid number for calories.")

    if st.button("Add Food"):
        if food_item and calories:
            st.session_state.daily_food_log.append({"item": food_item, "calories": calories})
            st.success(f"Added {food_item} with {calories} calories.")
        else:
            st.warning("Please enter both a food item and its calorie count.")

    st.write("### Today's Food Log")
    if st.session_state.daily_food_log:
        total_calories = sum([entry["calories"] for entry in st.session_state.daily_food_log])
        daily_calorie_goal_value = st.session_state.health_profile.get('daily_calorie_goal', 2000)

        st.metric(label="Consumed / Goal", value=f"{total_calories} / {daily_calorie_goal_value} calories")

        progress_ratio = min(total_calories / daily_calorie_goal_value, 1.0) if daily_calorie_goal_value > 0 else 0
        st.progress(progress_ratio, text=f"{(progress_ratio*100):.1f}% of daily goal")

        if total_calories < daily_calorie_goal_value:
            st.info(f"You are under your daily calorie goal by {daily_calorie_goal_value - total_calories} calories.")
        elif total_calories == daily_calorie_goal_value:
            st.success("Goal Met! You've reached your daily calorie goal.")
        else:
            st.warning(f"You have exceeded your daily calorie goal by {total_calories - daily_calorie_goal_value} calories.")

        for entry in st.session_state.daily_food_log:
            st.write(f"- {entry['item']}: {entry['calories']} calories")
        st.markdown(f"**Total Calories Today: {total_calories}**")
    else:
        st.info("No food items logged yet.")

    if st.button("Reset Daily Log"):
        st.session_state.daily_food_log = []
        st.rerun()

with tab5:
    st.subheader("Yoga for Wellness")

    yoga_query = st.text_input("Ask me about yoga poses or their benefits",
                               placeholder="e.g., 'What are the benefits of Downward Dog pose?'")

    if st.button("Get Yoga Insights"):
        if not yoga_query:
            st.warning("Please enter a question about yoga.")
        else:
            with st.spinner("Fetching yoga insights..."):
                prompt = f"""
                You are an expert yoga instructor and wellness coach.
                Provide detailed, comprehensive insights about the following yoga query:
                {yoga_query}

                Include:
                1. Clear explanation of the pose (if applicable).
                2. Step-by-step instructions for performing the pose (if applicable).
                3. Key physical and mental benefits.
                4. Any precautions or modifications.
                5. Suggestions for who might benefit most from this pose.

                Format the outputs clearly with headings and bullet points.
                """
                response = get_gemini_response(prompt)
                st.subheader("Yoga Insights")
                st.markdown(response)
