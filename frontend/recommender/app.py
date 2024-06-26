import os
import sys
import streamlit as st
import pandas as pd

# Navigate to root directory
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(root_dir)
real_project_dir = os.path.dirname(project_dir)

# Add project directory to Python path
sys.path.insert(0, real_project_dir)

# Import necessary functions from codecompasslib
from codecompasslib.models.lightgbm_model import generate_lightGBM_recommendations, load_data

# Function to load cached data
def load_cached_data():
    # Check if data is already stored in session state
    if 'cached_data' not in st.session_state:
        with st.spinner('Fetching data from the server...'):
            # Load data
            full_data_folder_id = '1Qiy9u03hUthqaoBDr4VQqhKwtLJ2O3Yd'
            full_data_embedded_folder_id = '139wi78iRzhwGZwxmI5WALoYocR-Rk9By'
            st.session_state.cached_data = load_data()
    return st.session_state.cached_data

def main():
    # Load the data
    df_non_embedded, df_embedded = load_cached_data()

    # Set app title
    st.title('GitHub Repo Recommendation System')

    # Input for target user
    target_user = st.text_input("Enter the target user's username:")

    # Multiselect for motivations
    st.subheader("What are your motivations for joining a project?")
    motivation_types = st.multiselect("Motivation Types", ["Learning", "Networking with others"],  default=["Learning", "Networking with others"])

    # Button to get recommendations
    if st.button('Get Recommendations'):
        # Check if user exists in the dataset
        if target_user not in df_embedded['owner_user'].values:
            st.error("User not found in the dataset. Please enter a valid username.")
        else:
            # Determine weights based on selected motivations
            supportive_env_weight = 1.0 if "Learning" in motivation_types else 0.0
            activity_weight = 1.0 if "Networking with others" in motivation_types else 0.0

            # Generate recommendations
            with st.spinner('Generating recommendations...'):
                recommendations = generate_lightGBM_recommendations(target_user, df_non_embedded, df_embedded,
                                                                   supportive_env_weight=supportive_env_weight,
                                                                   activity_weight=activity_weight,
                                                                   number_of_recommendations=10)
            
            # Display recommendations
            st.subheader("Recommendations")
            for index, repo in enumerate(recommendations):
                name = df_non_embedded[df_non_embedded['id'] == repo[0]]['name'].values[0]
                description = df_non_embedded[df_non_embedded['id'] == repo[0]]['description'].values[0]
                last_pushed_full = df_non_embedded[df_non_embedded['id'] == repo[0]]['date_pushed'].values[0]
                last_pushed = pd.to_datetime(last_pushed_full).date()
                has_wiki = df_non_embedded[df_non_embedded['id'] == repo[0]]['has_wiki'].values[0]
                has_discussion = df_non_embedded[df_non_embedded['id'] == repo[0]]['has_discussions'].values[0]
                stars = df_non_embedded[df_non_embedded['id'] == repo[0]]['stars'].values[0]
                link = f"https://github.com/{repo[1]}/{name}"

                # Determine the message to display for wiki availability
                if has_wiki or has_discussion:
                    wiki_message = "<span style='color: green;'>Available</span>"
                else:
                    wiki_message = "<span style='color: red;'>Unavailable</span>"

                # Display recommendation details in a card-like format with shadow
                st.markdown(f"""
                <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: #333; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);">
                    <h3 style="margin-bottom: 5px; color: #000;">{name}</h3>
                    <p style="color: #000;">{description}</p>
                    <h6 style="margin-bottom: 5px; color: #000;">⭐ received: {stars} </h6>
                    <h6 style="margin-bottom: 5px; color: #000;">Last updated: {last_pushed}</h6>
                    <h6 style="margin-bottom: 5px; color: #000;">Learning support: {wiki_message}</h6>
                    <a href="{link}" target="_blank" style="color: #0366d6; text-decoration: none;">View on GitHub</a>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
