import streamlit as st 
import pandas as pd  
import os  
import assignment2 

#function to load the list of countries from a CSV file
@st.cache_data  
def load_countries():
    data = pd.read_csv('a2-countries.csv')['country']
    return data.tolist()

st.title('A3 Test Runner')

#get input from the user for the sample ratio
#this is a number input where the default value is 1,000,000
SAMPLE_RATIO = st.number_input('Sample Ratio', value=1e6, format="%.2f")

#get the start date from the user, default is April 1, 2021
START_DATE = st.date_input('Start Date', value=pd.to_datetime('2021-04-01'))

#get the end date from the user, default is April 30, 2022
END_DATE = st.date_input('End Date', value=pd.to_datetime('2022-04-30'))

#load the list of countries from the CSV file (cached)
countries_list = load_countries()

#let the user pick one or more countries from the loaded list
SELECTED_COUNTRIES = st.multiselect('Select Countries', countries_list)

#adding a button that the user can press to run the process
if st.button('Run'):
    #checking if at least one country is selected
    if SELECTED_COUNTRIES:
        #converting the dates into string format because the 'run' function needs it
        start_date_str = START_DATE.strftime('%Y-%m-%d')
        end_date_str = END_DATE.strftime('%Y-%m-%d')
        #calling the run function from the 'assignment2' module
        assignment2.run(
            countries_csv_name='a2-countries.csv',
            countries=SELECTED_COUNTRIES,
            sample_ratio=SAMPLE_RATIO,
            start_date=start_date_str,
            end_date=end_date_str
        )
        #after running, we check if a simulation image was generated
        if os.path.exists('a2-covid-simulation.png'):
            st.image('a2-covid-simulation.png')
        else:
            st.error("Simulation image not found!")
    else:
        #if no countries are selected, show an error message
        st.error("Please select at least one country.")
