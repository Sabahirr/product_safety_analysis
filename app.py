import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from PIL import Image

# Ensure set_page_config is the first Streamlit command
icon = Image.open('icon.png')
logo = Image.open('logo.png')

st.set_page_config(layout = 'wide' ,
                   page_title="Sabahir's page" ,
                   page_icon = icon)

# Sidebar Container
st.sidebar.image(image = logo)
menu = st.sidebar.selectbox(f"Select 'Datasets' to get information about data, Select 'Dashboard' to see analysis results" , ['Datasets','Dashboard'])

# Load the datasets
injuries = pd.read_csv('injuries.csv')
products = pd.read_csv('products.csv')
population = pd.read_csv('population.csv')

if menu == 'Datasets':

    st.warning("""
               **Purpose**\n
               **The dataset is used for analyzing injury trends, identifying common causes of injuries, and understanding demographic patterns related to injury incidents. 
               It can be valuable for public health officials, safety regulators, and researchers focused on injury prevention and safety improvements.**\n
               
               **Potential Uses**\n
               Trend Analysis:  *Identifying trends over time in injury incidents.*\n
               Demographic Studies:  *Analyzing how injuries affect different age groups, and genders.*\n
               Safety Improvements:  *Identifying products or locations that are frequently associated with injuries to improve safety regulations and standards.*_\n
               Healthcare Research:  *Understanding the types of injuries that are most common and their diagnoses for better healthcare planning and resource allocation.*""")
    st.info("""
               **The dataset provides a comprehensive view of injury incidents and can be instrumental in developing strategies for injury prevention and improving public health and safety measures.
               The dataset provides detailed information about injury incidents. Each row in the dataset represents a single injury case with various attributes describing the circumstances, 
               demographics, and specifics of the injury.**\n
               **Columns:**\n
               trmt_date: *The date when the injury treatment occurred.*\n
               age: *The age of the individual who sustained the injury.*\n
               sex: *The gender of the individual (male or female).*\n
               race: *The race of the individual.*\n
               body_part: *The specific part of the body that was injured.*\n
               diag: *The diagnosis given for the injury.*\n
               location: *The location where the injury took place (e.g., home, work, school).*\n
               prod_code: *A product code associated with the injury, indicating the product involved in the incident.*\n
               weight: *The weight of the individual.*\n
               narrative: *A narrative description providing additional context or details about the injury.*\n
                   """)
    
    # Exploratory data analysis
    st.write(injuries.head())
    st.info("""
            **The dataset contains information about products, including their titles and associated codes.**\n
            **Columns:**\n
            prod_code: *Product code.*\n
            title: *Title or description of the product.*
            """)
    st.write(products.head())
    st.info("""
            **The dataset provides demographic information, specifically the population counts segmented by age and sex.**\n
            **Columns:**\n
            age: *Age of the population group.*\n
            sex: *Gender of the population group.*\n
            population: *The count of individuals in that age and sex group.*
            """)
    st.write(population.head())

else:
    # Convert trmt_date to datetime
    injuries['trmt_date'] = pd.to_datetime(injuries['trmt_date'])

    # Convert the date range to datetime.date
    min_date = injuries['trmt_date'].min().date()
    max_date = injuries['trmt_date'].max().date()


    # Most frequent product code
    pc = injuries['prod_code'].value_counts().idxmax()
    product_title = products.loc[products['prod_code'] == pc, 'title'].values[0]

    # Filter data for the most frequent product code
    stair_step = injuries[injuries['prod_code'] == 1842]

    # Plotting the data
    def plot_location(data, date_range, age_range):
        date_range = [pd.to_datetime(date) for date in date_range]
        filtered_data = data[(data['trmt_date'] >= date_range[0]) & (data['trmt_date'] <= date_range[1]) & 
                            (data['age'] >= age_range[0]) & (data['age'] <= age_range[1])]
        location_counts = filtered_data['location'].value_counts().reset_index()
        location_counts.columns = ['location', 'count']
        
        fig = go.Figure(data=[go.Pie(labels=location_counts['location'], values=location_counts['count'], hole=.3)])
        return fig

    def plot_diag(data, date_range, age_range):
        date_range = [pd.to_datetime(date) for date in date_range]
        filtered_data = data[(data['trmt_date'] >= date_range[0]) & (data['trmt_date'] <= date_range[1]) & 
                            (data['age'] >= age_range[0]) & (data['age'] <= age_range[1])]
        diag_counts = filtered_data['diag'].value_counts().reset_index()
        diag_counts.columns = ['diag', 'count']
        
        fig = px.bar(diag_counts, x='count', y='diag', orientation='h')
        return fig

    def plot_injuries_per(data, population, date_range, age_range):
        date_range = [pd.to_datetime(date) for date in date_range]
        filtered_data = data[(data['trmt_date'] >= date_range[0]) & (data['trmt_date'] <= date_range[1]) & 
                            (data['age'] >= age_range[0]) & (data['age'] <= age_range[1])]
        injuries_count = filtered_data.groupby(['age', 'sex']).size().reset_index(name='count')
        merged_data = pd.merge(injuries_count, population, on=['age', 'sex'], how='left')
        merged_data['rate'] = merged_data['count'] / merged_data['population'] * 10000
        
        fig = px.line(merged_data, x='age', y='rate', color='sex')
        fig.update_layout(yaxis_title='Injuries per 10000 people')
        return fig

    def plot_bodypart(data, date_range, age_range):
        date_range = [pd.to_datetime(date) for date in date_range]
        filtered_data = data[(data['trmt_date'] >= date_range[0]) & (data['trmt_date'] <= date_range[1]) & 
                            (data['age'] >= age_range[0]) & (data['age'] <= age_range[1])]
        bodypart_counts = filtered_data['body_part'].value_counts().reset_index()
        bodypart_counts.columns = ['body_part', 'count']
        
        fig = px.bar(bodypart_counts, x='count', y='body_part', orientation='h')
        return fig

    # Streamlit UI
    st.title('Consumer Product Safety Commission')
    st.write('Product causing the most injuries: ', product_title)

    date_range = st.slider('When the person was seen in hospital', 
                        min_value=min_date, 
                        max_value=max_date, 
                        value=(min_date, max_date), 
                        format="MM/DD/YYYY")

    age_range = st.slider('Age of patients:', int(stair_step['age'].min()), int(stair_step['age'].max()), (20, 45))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Places where the accident occurred:')
        st.plotly_chart(plot_location(stair_step, date_range, age_range))

    with col2:
        st.subheader('Basic diagnosis of injury:')
        st.plotly_chart(plot_diag(stair_step, date_range, age_range))

    col3, col4 = st.columns([7, 5])

    with col3:
        st.subheader('Injuries per 10000 people:')
        st.plotly_chart(plot_injuries_per(stair_step, population, date_range, age_range))

    with col4:
        st.subheader('Location of the injury on the body:')
        st.plotly_chart(plot_bodypart(stair_step, date_range, age_range))
