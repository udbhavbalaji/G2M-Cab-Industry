import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)

# Reading in Cab_Data.csv data to filter out the columns that we want to analyze
cab_data = pd.read_csv('Datasets/Cab_Data.csv')
cab_data.columns = ['txnID','travel_date','company','city','travel_distance','price','cost']

# Let's create a column for profit for each individual ride
cab_data['profit'] = cab_data['price'] - cab_data['cost']

# # Let us gather columns that we want to explore into a separate dataframe
# From cab_data, all the columns except the travel_date are relavant and would be interesting to explore
final_df = cab_data[['company','city','travel_distance','price','cost','profit']]
final_df.index = cab_data['txnID']

# Reading in City.csv data to filter out and add the required data into final_df, so that we can analyze this data
city = pd.read_csv('Datasets/City.csv')
city.columns = ['city','population','users']
city = city.set_index('city')

# We see that we have the population and cab users of each city 
# Using this, we can create a user_ratio, giving us information about what proportion of the data are cab users.
# user_ratio can be used to evaluate the current market for cabs in a city as well as potential for future growth

# Since both the population and users fields are strings, we first need to convert them into floats before calculating user_ratio
city['population'] = city['population'].str.replace(',', '')
city['users'] = city['users'].str.replace(',', '')
city['population'] = city['population'].apply(lambda x: float(x.strip()))
city['users'] = city['users'].apply(lambda x: float(x.strip()))
city['user_ratio'] = city['users'] / city['population']

# We need this information (poopulation and user_ratio) added to final_df too. But the length of the dataframes are unequal. This is because of the presence of 
# multiple rides that took place in the same city. As a result, we will add the data for a particular city to each ride with that city in final_df.
pop_list = []
ratio_list = []
pop_dict = {}
for index,row in city.iterrows():
    pop_dict[index] = [row['population'],row['user_ratio']]

final_df = final_df.copy()
final_df['population'] = 0
final_df['user_ratio'] = 0
city_list = list(final_df['city'])

for cities in city_list:
    pop_list.append(pop_dict[cities][0])
    ratio_list.append(pop_dict[cities][1])

final_df['population'] = final_df.apply(lambda x:pop_list)
final_df['user_ratio'] = final_df.apply(lambda x:ratio_list)

# Reading in Transaction_ID.csv to filter out and add the required data to final_df, so that we can analyze this data
transactions = pd.read_csv('Datasets/Transaction_ID.csv')
transactions.columns = ['txnID','custID','mode_payment']
transactions = transactions.set_index('txnID')

# txnID has been set as the index for the final_df dataframe. We also need the custID field in order to add data from Customer_ID.csv to final_df.
# Mode of paymnent is a really useful piece of information to analyze as well. Since transactions and final_df are of same length with txnID as the 
# index, we can just perform inner merge to obtain the customer id for each ride as well as the mode pf payment.
final_df = pd.merge(final_df, transactions, how='inner', left_index=True, right_index=True)

# Reading in Customer_ID.csv to filter out and add the required data fields to final_df, so that we can analyze the entire relavant data
customer = pd.read_csv('Datasets/Customer_ID.csv')
customer.columns = ['custID','gender','age','income_per_month_dollars']
customer = customer.set_index('custID')

# It is intuituve that each customer might not necessarily have only one trip in a cab. Therefore, the lengths of final_df and customer are of 
# different lengths. Just like the problem with City.csv, we will insert the following personal details of the customer in each record of final_df where that particular
# customer has taken a ride.
final_df = final_df.copy()
final_df['gender'] = 0
final_df['age'] = 0
final_df['income_per_month'] = 0
cust_list = list(final_df['custID'])

cust_dict = {}
for index, row in customer.iterrows():
    cust_dict[index] = [row['gender'], row['age'], row['income_per_month_dollars']]
    
gender_list = []
age_list = []
income_list = []

for customers in cust_list:
    gender_list.append(cust_dict[customers][0])
    age_list.append(cust_dict[customers][1])
    income_list.append(cust_dict[customers][2])
    
final_df['gender'] = final_df.apply(lambda x:gender_list)
final_df['age'] = final_df.apply(lambda x:age_list)
final_df['income_per_month'] = final_df.apply(lambda x:income_list)

# Another possible route that we might want to explore is to split the location names into cities and states so that
#  we can get more information regarding a company's performance in a particular state.

final_df['state'] = final_df['city'].apply(lambda x: x.strip()[-2:] if x not in ['SILICON VALLEY','ORANGE COUNTY'] else 'LA')
final_df['city'] = final_df['city'].apply(lambda x: x.strip()[:-2].strip() if x not in ['SILICON VALLEY','ORANGE COUNTY'] else x.strip())

# We have now created the master data. We will export this into a .csv file, which we will further explore in our EDA notebook
print(final_df[final_df.city == 'SILICON VALLEY'].head())
final_df.to_csv('Datasets/Master_Data.csv')