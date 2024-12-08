from sim_parameters import TRANSITION_PROBS, HOLDING_TIMES
import pandas as pd
import random

#reading the countries data from the CSV file and returning it as a DataFrame
def read_countries_data(file):
    return pd.read_csv(file)

#creating the sample population based on the selected countries and the sample ratio
def create_sample_population(countries_df, selected_countries, sample_ratio):
    population = [] 
    person_id = 0  

    #looping through each selected country
    for country in selected_countries:
        country_data = countries_df[countries_df['country'] == country]  
        population_size = int(country_data['population'].values[0])  
        
        #defining the age groups for the population
        age_groups = ['less_5', '5_to_14', '15_to_24', '25_to_64', 'over_65']
        
        #looping through each age group to calculate the population sample for that group
        for age_group in age_groups:
            percentage = country_data[age_group].values[0] / 100  
            group_size = int(population_size * percentage / sample_ratio)  
            
            # Looping to add individuals for this age group to the population list
            for _ in range(group_size):
                population.append({
                    'person_id': person_id,  
                    'country': country,  
                    'age_group': age_group,  
                    'state': 'H',  
                    'staying_days': 0  
                })
                person_id += 1  
    
    return population  

# Initializing the time series data for each individual over the specified date range
def initialize_timeseries(population, start_date, end_date):
    data = []  
    date_range = pd.date_range(start=start_date, end=end_date)  
    
    # Looping through each individual in the population
    for individual in population:
        # Looping through each date in the date range
        for date in date_range:
            # Appending a new record for each individual and each date
            data.append({
                'person_id': individual['person_id'],  
                'age_group': individual['age_group'], 
                'country': individual['country'], 
                'date': date,
                'state': 'H',  
                'staying_days': 0  
            })
    
    # Converting the data list into a DataFrame and returning it
    timeseries = pd.DataFrame(data)
    return timeseries

# Simulating the state transitions for each individual based on the Markov Chain
def simulate_individual(timeseries, TRANSITION_PROBS, HOLDING_TIMES):
    person_id = 0 
    current_state = 'H' 
    holding_time = 0  

    # Looping through each row in the time series DataFrame
    for index, row in timeseries.iterrows():
        age_group = row['age_group']  

        # Checking if we're encountering a new individual
        if row['person_id'] != person_id:
            person_id = row['person_id'] 
            current_state = 'H'  
            holding_time = 0  

        # If the individual’s holding time has ended, transitioning them to the next state
        if holding_time <= 0:
            # Determining the next state based on transition probabilities
            next_state_probs = TRANSITION_PROBS[age_group][current_state]
            next_state = random.choices(list(next_state_probs.keys()), list(next_state_probs.values()))[0]

            # Updating the current state and setting the holding time for the new state
            current_state = next_state
            holding_time = HOLDING_TIMES[age_group][next_state]
        
        # Storing the updated state and holding time back into the DataFrame
        timeseries.at[index, 'state'] = current_state
        timeseries.at[index, 'staying_days'] = holding_time

        # Reducing the holding time by 1 as we move to the next day
        holding_time -= 1

    return timeseries  

# Saving the time series data to a CSV file
def save_timeseries(timeseries, filename='a2-covid-simulated-timeseries.csv'):
    timeseries.to_csv(filename, index=False)

# Summarizing the states for each country on each date
def summarize_states(timeseries):
    # Grouping the time series by country, date, and state and counting the occurrences
    groupedby_timeseries = timeseries.groupby(['country', 'date', 'state']).agg(
        {'state': len}).rename(columns={'state': 'count'}).reset_index()

    # Pivoting the data to get 'D', 'H', 'I', 'M', 'S' states as columns
    summarized_timeseries = pd.pivot(groupedby_timeseries, index=['date', 'country'], 
                                     columns='state', values='count').fillna(0).astype('int')

    # Making sure that all expected states ('D', 'H', 'I', 'M', 'S') are present in the summary
    for state in ['D', 'H', 'I', 'M', 'S']:
        if state not in summarized_timeseries.columns:
            summarized_timeseries[state] = 0  # Adding missing states with a value of 0

    # Reordering the columns to match the required format
    summarized_timeseries = summarized_timeseries[['D', 'H', 'I', 'M', 'S']]

    # Resetting the index to bring 'date' and 'country' back as columns
    summarized_timeseries.reset_index(inplace=True)

    # Saving the summary to a CSV file
    summarized_timeseries.to_csv('a2-covid-summary-timeseries.csv', index=False)

    return summarized_timeseries  # Returning the summary

# Saving the summarized states to a CSV file
def save_summary(summary, filename='a2-covid-summary-timeseries.csv'):
    summary.to_csv(filename, index=False)

from helper import create_plot

# Generating the plot based on the summarized data and selected countries
def generate_plot(summary_file, countries):
    create_plot(summary_file, countries)

# Main function to run the entire simulation process and generate outputs
def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    countries_df = read_countries_data(countries_csv_name)
    population = create_sample_population(countries_df, countries, sample_ratio)
    timeseries = initialize_timeseries(population, start_date, end_date)
    timeseries = simulate_individual(timeseries, TRANSITION_PROBS, HOLDING_TIMES)
    save_timeseries(timeseries)
    summary = summarize_states(timeseries)
    save_summary(summary)
    generate_plot('a2-covid-summary-timeseries.csv', countries)
