from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import pandas as pd
from country_codes import eurostat_dictionary
import eurostat
import matplotlib.pyplot as plt
from dowhy.causal_identifier import backdoor

from warnings import filterwarnings
filterwarnings('ignore')

EU_countries = ['Belgium', 'Bulgaria', 'Czechia', 'Denmark',
'Germany (until 1990 former territory of the FRG)', 'Germany','Estonia',
'Ireland', 'Greece', 'Spain', 'France', 'Croatia', 'Italy',
'Cyprus', 'Latvia', 'Lithuania', 'Luxembourg', 'Hungary', 'Malta',
'Netherlands', 'Austria', 'Poland', 'Portugal', 'Romania',
'Slovenia', 'Slovakia', 'Finland', 'Sweden', 'United Kingdom',
'Iceland', 'Liechtenstein', 'Norway', 'Switzerland',
'Bosnia and Herzegovina']

COUNTRY = "Netherlands"

# Outcome variable
def youth_at_home(COUNTRY, SEX = None, AGE = None):
    df_n = eurostat.get_data_df('ilc_lvps08') # YOUNG PEOPLE LIVING AT HOME
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)
    df_n.drop(['unit', 'freq'],axis=1,inplace=True)
    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n.drop(['geo'],axis=1,inplace=True)
    df_n = df_n[df_n['country'] == COUNTRY]
    df_n.set_index(['sex', 'age', 'country'], inplace=True)
    return df_n


# Unemployment by age, sex, citizenship
def unemployment(COUNTRY):
    df_n = eurostat.get_data_df('lfsa_urgan') 
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)

    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n = df_n[df_n['country'] == COUNTRY]
    df_n = df_n[df_n['citizen'] =='NAT']
    
    df_n.drop(['geo', 'freq', 'unit', 'citizen'],axis=1,inplace=True)
    ages = ['Y15-19', 'Y15-24', 'Y15-29', 'Y15-39', 'Y20-24', 'Y20-29', 'Y25-29', 'Y30-34' ]
    # keep only these ages
    df_n.set_index(['sex', 'age', 'country'], inplace=True)
    df_n= df_n[df_n.index.get_level_values('age').isin(ages)]
    df_n= df_n[['2010', '2020']]
    return df_n


# Mobile students from abroad enrolled by education level, sex and country of origin
def mobile_students_from_abroad(COUNTRY):
    df_n = eurostat.get_data_df('educ_uoe_mobs02')
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)
    df_n.drop(['partner', 'freq', 'unit'],axis=1,inplace=True)
    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n.drop(['geo'],axis=1,inplace=True)
    df_n = df_n[df_n['country'] == COUNTRY]
    df_n = df_n[df_n['isced11'] == 'ED5-8']
    df_n = df_n[df_n['sex'] == 'T'] 
    df_n.drop(['isced11'],axis=1,inplace=True)
    df_n.set_index(['sex', 'country'], inplace=True)
    df_n = df_n.sum(axis=0)
    df_n = df_n.T
    return df_n

# Inward mobile students as percentage of student population in the host country (%)
def students_from_abroad_by_level_and_field(COUNTRY):
    df_n = eurostat.get_data_df('educ_momo_fld')
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)
    # df_n.drop(['unit', 'freq'],axis=1,inplace=True)
    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n.drop(['geo'],axis=1,inplace=True)
    df_n = df_n[df_n['country'] == COUNTRY]
    df_n = df_n[df_n['field'] == 'TOTAL']
    df_n = df_n[df_n['indic_ed'] == 'MS01_2P']

    return df_n

# Gereguleerde huurwoningen (%) CBS
def huurwoningen_NL():
    file_path = 'table_tabel-1c5c9e98-d6b6-4a91-99a4-52fa29f14feb.csv'
    huurwoningen_df= pd.read_csv(file_path, sep=',')
    huurwoningen_df = huurwoningen_df[['Gereguleerde huurwoningen1) (%)', 'categories1']]
    huurwoningen_df = huurwoningen_df[huurwoningen_df['categories1'].isin(['2012', '2021'])]
    return huurwoningen_df

# Average student debt per age category
def student_debt():
    file_path = 'table_tabel-ef26b4a9-7b08-42a9-b76c-a50afbfde19c.csv'
    student_debt_df= pd.read_csv(file_path, sep=',')
    student_debt_df = student_debt_df[student_debt_df['Jaar'].isin(['2011', '2020'])]
    return student_debt_df


# Students enrolled in tertiary education by education level, programme orientation, sex and age
# in absolute numbers
def students_tertiary_eduction(COUNTRY):
    df_n = eurostat.get_data_df('educ_uoe_enrt02')
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)
    df_n.drop(['freq', 'unit'],axis=1,inplace=True)
    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n.drop(['geo'],axis=1,inplace=True)
    df_n = df_n[df_n['country'] == COUNTRY]
    df_n = df_n[df_n['isced11'] == 'ED5-8']
    df_n = df_n[df_n['age'] == 'TOTAL']
    df_n.set_index(['sex', 'age', 'country'], inplace=True)

    return df_n

# OUTCOME VARIABLE
# Share of young adults aged 18-34 living with their parents by self-defined current economic status - EU-SILC survey (
def share_young_with_parents(COUNTRY):
    """
    # Employed persons working full-time
    # [EMP_FT]
    # Employed persons working part-time
    # [EMP_PT]
    # Unemployed persons
    # [UNE]
    # Students
    # [EDUC]
    # Other persons outside the labour force (former name: inactive persons)
    # [INAC_OTH]
    """
    df_n = eurostat.get_data_df('ilc_lvps09')
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)
    df_n.drop(['unit', 'freq'],axis=1,inplace=True)
    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n.drop(['geo'],axis=1,inplace=True)
    df_n = df_n[df_n['country'] == COUNTRY]
    df = df_n[['country', 'age','wstatus', '2010']]
    df_outcome_2010 = df
    df = df_n[['country', 'age','wstatus', '2020']]
    df_outcome_2020 = df
    return df_outcome_2010, df_outcome_2020

def first_time_marrying(COUNTRY):
    df_n = eurostat.get_data_df('demo_nsinagec')
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)

    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n.drop(['geo'],axis=1,inplace=True)
    df_n.drop(['freq'],axis=1,inplace=True)
    # df_n = df_n[df_n['unit'] == 'PC']
    # df_n = df_n[df_n['sex'] == 'T']
    df_n = df_n[df_n['country'] == COUNTRY]
    df_n['age'].unique()

    ages = ['Y25-29', 'Y20-24', 'Y30-34', 'Y15-19']

    df_n.set_index(['age', 'country'], inplace=True)
    df_n= df_n[df_n.index.get_level_values('age').isin(ages)]
    df_n= df_n[['2010', '2020']]
    # Y18-34 : 'Y20-24' + 'Y25-29' + 'Y30-34'
    young_people_married = df_n
    young_people_married = young_people_married.reset_index()
    young_people_married = young_people_married.groupby(['age', 'country']).sum()
    return young_people_married


# Monthly minimum wage as a proportion of average monthly earnings (%) - NACE Rev. 2 (from 2008 onwards)
def minimum_wage(COUNTRY):
    df_n = eurostat.get_data_df('earn_mw_avgr2')
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)

    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n.drop(['geo', 'freq', 'unit'],axis=1,inplace=True)

    df_n = df_n[df_n['indic_se'] == 'MMW_MEAN_ME_PP']
    df_n = df_n[df_n['country'] == COUNTRY]
    df_n = df_n[df_n['nace_r2'] == 'B-N']

    return df_n

# Rent price evolution
def rent_price_evolution(COUNTRY):
    ''' Rent evolution - Annual average index - Actual rentals for housing'''
    df_n = eurostat.get_data_df('prc_hicp_aind')
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)

    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n.drop(['geo', 'freq'],axis=1,inplace=True)
    df_n = df_n[df_n['country'] == COUNTRY]

    df_n = df_n[df_n['coicop'] == 'CP041']
    df_n = df_n[df_n['unit'] == 'INX_A_AVG']
    
    return df_n

def total_inflation(COUNTRY):

    df_n = eurostat.get_data_df('prc_hicp_aind')
    df_n.rename({'geo\TIME_PERIOD':'geo'},inplace=True,axis=1)

    df_n['country'] = df_n['geo'].replace(eurostat_dictionary)
    df_n.drop(['geo', 'freq'],axis=1,inplace=True)
    df_n = df_n[df_n['country'] == COUNTRY]

    df_n = df_n[df_n['coicop'] == 'CP00']
    df_n = df_n[df_n['unit'] == 'INX_A_AVG']
    return df_n


def calculate_average_student_debt_2011_NL(student_debt_df):
    # Calculate average student debt based on age groups
    student_debt_df_2011 = student_debt_df[student_debt_df['Jaar'] == '2011']
    
    total_student_debt_NL = 9.5 * 1000000000

    val = float(str(student_debt_df_2011.loc[student_debt_df_2011.index[0], '20 tot 25 jaar (1 000 euro)']).replace(',', '.')) * 1000
    average_student_debt_18_24 = val 

    val = float(str(student_debt_df_2011.loc[student_debt_df_2011.index[0], '25 tot 30 jaar (1 000 euro)']).replace(',', '.')) * 1000 + val
    average_student_debt_18_34 = val / 2

    val = float(str(student_debt_df_2011.loc[student_debt_df_2011.index[0], '25 tot 30 jaar (1 000 euro)']).replace(',', '.')) * 1000 + float(str(student_debt_df_2011.loc[student_debt_df_2011.index[0], '30 jaar en ouder (1 000 euro)']).replace(',', '.')) * 1000 
    average_student_debt_25_34 = val / 2

    return average_student_debt_18_24, average_student_debt_18_34, average_student_debt_25_34, total_student_debt_NL



def process_outcome_2010(df_outcome_2010, rentals_df, total_inflation_df, minimum_wage_PC, young_people_married, huurwoningen_df, mobile_students_from_abroad_df, student_debt_df):
    # Adding a new column based on conditions
    df_outcome_2010['unemployment_rate_age_group'] = None
    df_outcome_2010.loc[df_outcome_2010['age'] == 'Y18-34', 'unemployment_rate_age_group'] = 5.9
    df_outcome_2010.loc[df_outcome_2010['age'] == 'Y18-24', 'unemployment_rate_age_group'] = 10.8
    df_outcome_2010.loc[df_outcome_2010['age'] == 'Y25-34', 'unemployment_rate_age_group'] = 3.7
    
    df_outcome_2010['youth_getting_married'] = None
    df_outcome_2010.loc[df_outcome_2010['age'] == 'Y18-34', 'youth_getting_married'] = young_people_married[young_people_married.index.get_level_values('age') == 'Y20-24']['2010'][0] +  young_people_married[young_people_married.index.get_level_values('age') == 'Y25-29']['2010'][0] + +  young_people_married[young_people_married.index.get_level_values('age') == 'Y30-34']['2010'][0]
    df_outcome_2010.loc[df_outcome_2010['age'] == 'Y18-24', 'youth_getting_married'] = young_people_married[young_people_married.index.get_level_values('age') == 'Y20-24']['2010'][0]
    df_outcome_2010.loc[df_outcome_2010['age'] == 'Y25-34', 'youth_getting_married'] = young_people_married[young_people_married.index.get_level_values('age') == 'Y25-29']['2010'][0] +  young_people_married[young_people_married.index.get_level_values('age') == 'Y30-34']['2010'][0]

    df_outcome_2010['rent_price_index'] = rentals_df.iloc[0]['2010']
    df_outcome_2010['inflation_index'] = total_inflation_df.iloc[0]['2010']
    df_outcome_2010['minimum_wage_PC_mean_income'] = minimum_wage_PC.iloc[0]['2010']
    df_outcome_2010['mobile_students_from_abroad'] = mobile_students_from_abroad_df['2013']


    if COUNTRY == 'Netherlands':

        huurwoningen_2012 = huurwoningen_df[huurwoningen_df['categories1'] == '2012']
        df_outcome_2010['PC_eating_fruit'] = None  #15 to 29 YRS	  (24.7)	
        df_outcome_2010.loc[df_outcome_2010['age'] == 'Y18-24', 'PC_eating_fruit'] = 17.9
        df_outcome_2010['Regulated rental dwellings (%)'] = huurwoningen_2012.loc[huurwoningen_2012.index[0], 'Gereguleerde huurwoningen1) (%)']

        average_student_debt_18_24, average_student_debt_18_34, average_student_debt_25_34, total_student_debt_NL = calculate_average_student_debt_2011_NL(student_debt_df)
        df_outcome_2010['average_student_debt'] = None 
        df_outcome_2010['total_student_debt_NL'] = total_student_debt_NL
        df_outcome_2010.loc[df_outcome_2010['age'] == 'Y18-24', 'average_student_debt'] = average_student_debt_18_24
        df_outcome_2010.loc[df_outcome_2010['age'] == 'Y18-34', 'average_student_debt'] = average_student_debt_18_34
        df_outcome_2010.loc[df_outcome_2010['age'] == 'Y25-34', 'average_student_debt'] = average_student_debt_25_34

        df_outcome_2010['gemiddelde_verkoopprijs_woning'] = 239.530 #https://www.cbs.nl/nl-nl/cijfers/detail/83906NED?dl=64BA2
        
    return df_outcome_2010


def calculate_average_student_debt_2020_NL(student_debt_df):
    student_debt_df_2020 = student_debt_df[student_debt_df['Jaar'] == '2020']

    total_student_debt_NL = 23.1 * 1000000000

    val = float(str(student_debt_df_2020.loc[student_debt_df_2020.index[0], '20 tot 25 jaar (1 000 euro)']).replace(',', '.')) * 1000
    average_student_debt_18_24 = val 

    val = float(str(student_debt_df_2020.loc[student_debt_df_2020.index[0], '25 tot 30 jaar (1 000 euro)']).replace(',', '.')) * 1000 + val
    average_student_debt_18_34 = val / 2

    val = float(str(student_debt_df_2020.loc[student_debt_df_2020.index[0], '25 tot 30 jaar (1 000 euro)']).replace(',', '.')) * 1000 + float(str(student_debt_df_2020.loc[student_debt_df_2020.index[0], '30 jaar en ouder (1 000 euro)']).replace(',', '.')) * 1000 
    average_student_debt_25_34 = val / 2

    return average_student_debt_18_24, average_student_debt_18_34, average_student_debt_25_34, total_student_debt_NL


def process_outcome_2020(df_outcome_2020, rentals_df, total_inflation_df, minimum_wage_PC, young_people_married, huurwoningen_df, mobile_students_from_abroad_df, student_debt_df):
    # Adding a new column based on conditions
    df_outcome_2020['unemployment_rate_age_group'] = None
    df_outcome_2020.loc[df_outcome_2020['age'] == 'Y18-34', 'unemployment_rate_age_group'] = 5.0
    df_outcome_2020.loc[df_outcome_2020['age'] == 'Y18-24', 'unemployment_rate_age_group'] = 8.7
    df_outcome_2020.loc[df_outcome_2020['age'] == 'Y25-34', 'unemployment_rate_age_group'] = 3.2

    df_outcome_2020['youth_getting_married'] = None
    df_outcome_2020.loc[df_outcome_2020['age'] == 'Y18-34', 'youth_getting_married'] = young_people_married[young_people_married.index.get_level_values('age') == 'Y20-24']['2020'][0] +  young_people_married[young_people_married.index.get_level_values('age') == 'Y25-29']['2020'][0] + +  young_people_married[young_people_married.index.get_level_values('age') == 'Y30-34']['2020'][0]
    df_outcome_2020.loc[df_outcome_2020['age'] == 'Y18-24', 'youth_getting_married'] = young_people_married[young_people_married.index.get_level_values('age') == 'Y20-24']['2020'][0]
    df_outcome_2020.loc[df_outcome_2020['age'] == 'Y25-34', 'youth_getting_married'] = young_people_married[young_people_married.index.get_level_values('age') == 'Y25-29']['2020'][0] +  young_people_married[young_people_married.index.get_level_values('age') == 'Y30-34']['2020'][0]

    df_outcome_2020['rent_price_index'] = rentals_df.iloc[0]['2020']

    df_outcome_2020['PC_eating_fruit'] = None 
    df_outcome_2020.loc[df_outcome_2020['age'] == 'Y18-24', 'PC_eating_fruit'] = 24.7

    df_outcome_2020['mobile_students_from_abroad']  = mobile_students_from_abroad_df['2020']

    df_outcome_2020['minimum_wage_PC_mean_income'] = minimum_wage_PC.iloc[0]['2020']
    
    df_outcome_2020['inflation_index'] = total_inflation_df.iloc[0]['2020']


    if COUNTRY == 'Netherlands':

        huurwoningen_2021 = huurwoningen_df[huurwoningen_df['categories1'] == '2021']
        df_outcome_2020['Regulated rental dwellings (%)'] = huurwoningen_2021.loc[huurwoningen_2021.index[0], 'Gereguleerde huurwoningen1) (%)'] 

        df_outcome_2020['average_student_debt'] = None
        average_student_debt_18_24, average_student_debt_18_34, average_student_debt_25_34, total_student_debt_NL = calculate_average_student_debt_2020_NL(student_debt_df)
        df_outcome_2020['total_student_debt_NL'] = total_student_debt_NL
        df_outcome_2020.loc[df_outcome_2020['age'] == 'Y18-24', 'average_student_debt'] = average_student_debt_18_24
        df_outcome_2020.loc[df_outcome_2020['age'] == 'Y18-34', 'average_student_debt'] = average_student_debt_18_34
        df_outcome_2020.loc[df_outcome_2020['age'] == 'Y25-34', 'average_student_debt'] = average_student_debt_25_34

        df_outcome_2020['gemiddelde_verkoopprijs_woning'] = 334.488
    return df_outcome_2020


def process_country(COUNTRY):
    total_inflation_df = total_inflation(COUNTRY)
    rentals_df = rent_price_evolution(COUNTRY)
    
    minimum_wage_PC = minimum_wage(COUNTRY)
    young_people_married = first_time_marrying(COUNTRY)
    tertiary_education = students_tertiary_eduction(COUNTRY)

    huurwoningen_df = huurwoningen_NL()
    student_debt_df = student_debt()

    students_from_abroad_PC = students_from_abroad_by_level_and_field(COUNTRY)
    mobile_students_from_abroad_df = mobile_students_from_abroad(COUNTRY)
    df_n_unemployment_rate_PC = unemployment(COUNTRY)

    df = youth_at_home(COUNTRY , SEX = None, AGE = None)

    df_outcome_2010, df_outcome_2020 = share_young_with_parents(COUNTRY)
 
    df_outcome_2020 = process_outcome_2020(df_outcome_2020, rentals_df, total_inflation_df, minimum_wage_PC, young_people_married, huurwoningen_df, mobile_students_from_abroad_df, student_debt_df)
    df_outcome_2010 = process_outcome_2010(df_outcome_2010, rentals_df, total_inflation_df, minimum_wage_PC, young_people_married, huurwoningen_df, mobile_students_from_abroad_df, student_debt_df)
    return df_outcome_2010, df_outcome_2020

df_outcome_2010, df_outcome_2020 = process_country('Netherlands')
print(df_outcome_2010)
  

  


