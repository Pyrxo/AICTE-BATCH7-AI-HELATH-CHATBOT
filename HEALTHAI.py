from logging import warning
import os
import google.generativeai as genai
from PIL import Image
import streamlit as st

GOOGLE_API_KEY="AIzaSyCQ-4nPm3-QQWixZz16Ab9X0YhpxZKU" # Replaced with a placeholder key for security
genai.configure(api_key=GOOGLE_API_KEY)

if'health_profile' not in st.session_state:
    st.session_state.health_profile ={
        'goals': 'lose 10 pounds in 3 months\nImprove cardiovascular health',
        'conditions': 'none',
        'routines' : '30-minute walk 3x/week',
        'restrictions': 'vegetarian\nLow carb',
        'preferences': '', # Added for consistency
    }

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

    if st.button("Update Profile"):
        st.session_state.health_profile ={
        'goals': health_goals,
        'conditions': medical_conditions,
        'routines' : fitness_routines,
        'preferences': food_preferences, # Corrected key from 'prefrences'
        'restrictions': restrictions,
        }
        st.success("Profile updated!")
tab1, tab2,tab3 =st.tabs(["Meal Planning","Food Analysis","Health Insights"])

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
                User specific requirements: {user_inputs}
                Additional requirements : {user_inputs if user_inputs else 'None'}

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
          st.warning("please enter a health question")
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
