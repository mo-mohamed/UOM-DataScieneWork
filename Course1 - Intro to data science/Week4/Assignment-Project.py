import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import re as regex

pd.set_option('display.max_columns', 20)
pd.set_option("display.width", 900)
pd.set_option('max_colwidth',40)
pd.set_option('display.max_rows', 1000)


#Decalre file pathes
university_towns_file = r"C:\Users\mosta\Desktop\Coursera - Data Science Track\Project\Files\university_towns.txt"
gdb_file = r"C:\Users\mosta\Desktop\Coursera - Data Science Track\Project\Files\gdplev.xls"
housing_file = r"C:\Users\mosta\Desktop\Coursera - Data Science Track\Project\Files\City_Zhvi_AllHomes.csv"


def get_list_of_university_towns():

    with open(university_towns_file) as f:
        content = [line.rstrip('\n') for line in f.readlines()]  # read and strip new lines characaters..
        result = [] #our result, we append tuples containing state and region names
        current_state = ""
        for line in content: #remember current state
            # starte processing, we need to check if state or city
            if "[edit]" in line:
                #Ok we have a state
                current_state = regex.sub(r'\[.*?\]', '', line)
            else:
                #OK we have a region
                region_name = regex.sub(r'\(.*', '', line).strip() # clean names
                result.append((current_state, region_name))

        df = pd.DataFrame(result, columns=["State", "RegionName"])
        return df

def prepare_gdp_frame():
    frame = pd.read_excel(gdb_file, skiprows=219, usecols=[4, 6])
    frame.columns = ['Quarter', 'GDP']
    frame["GDP change"] = frame["GDP"].diff()
    return frame



def get_recession_start():
    frame = prepare_gdp_frame()
    for i in range(len(frame)-1):
        if (frame.iloc[i + 2]["GDP change"] < frame.iloc[i+1]["GDP change"]) and (frame.iloc[i+1]["GDP change"] < frame.iloc[i]["GDP change"]):
            return frame.iloc[i][0]


def get_recession_end():
    frame = prepare_gdp_frame()
    starte_index = get_recession_start()
    start_position = frame[frame["Quarter"] == starte_index].index.tolist()[0]
    frame = frame.iloc[start_position:]
    for i in range(len(frame) - 1):
        if (frame.iloc[i+2]["GDP change"] > frame.iloc[i+1]["GDP change"]) and (frame.iloc[i+1]["GDP change"] > 0):
            return frame.iloc[i][0]


def get_recession_bottom():
    frame = prepare_gdp_frame()
    start_position = frame[frame["Quarter"] == get_recession_start()].index.tolist()[0]
    end_position = frame[frame["Quarter"] == get_recession_end()].index.tolist()[0]
    frame = frame.iloc[start_position:end_position+1]
    bottom_index = frame["GDP"].idxmin()
    return frame.iloc[bottom_index - start_position]["Quarter"]


def new_col_names():
    #generating the new coloumns names
    years = list(range(2000,2017))
    quars = ['q1','q2','q3','q4']
    quar_years = []
    for i in years:
        for x in quars:
            quar_years.append((str(i)+x))
    return quar_years[:67]

def convert_housing_data_to_quarters():
    states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National',
              'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana',
              'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho',
              'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan',
              'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi',
              'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota',
              'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut',
              'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York',
              'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado',
              'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota',
              'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia',
              'ND': 'North Dakota', 'VA': 'Virginia'}

    frame = pd.read_csv(housing_file)
    frame.drop(['Metro', 'CountyName', 'RegionID', 'SizeRank'], axis=1, inplace=True)
    frame['State'] = frame['State'].map(states)
    frame = frame.set_index(["State", "RegionName"])

    frame.columns = pd.to_datetime(frame.columns)
    mdf = frame[frame.columns].resample('Q', axis=1).mean().rename(columns=lambda x: str(x.to_period('Q')).lower())
    mdf = mdf[new_col_names()]

    return  mdf



def run_ttest():
    housing_frame = convert_housing_data_to_quarters()
    univerty_towns = get_list_of_university_towns()
    # university_towns = get_list_of_university_towns().values
    # university_towns = [tuple(l) for l in university_towns]
    quarter_before_recession = get_recession_start()
    recession_bottom = get_recession_bottom()

    housing_frame = housing_frame[[quarter_before_recession, recession_bottom]]
    housing_frame["price_ratio"] = housing_frame[quarter_before_recession] / housing_frame[recession_bottom]


    mergedFrames = housing_frame.merge(univerty_towns,how = "left", left_index = True, right_on=["State", "RegionName"], indicator = True)
    mergedFrames["isUni"] = mergedFrames["_merge"].apply(lambda x: 0 if x == "left_only" else 1)
    university_towns_frame = mergedFrames[mergedFrames["isUni"] == 1]
    non_university_towns_frame = mergedFrames[mergedFrames["isUni"] == 0]

    t_stat, p_value = ttest_ind(university_towns_frame["price_ratio"],
                                non_university_towns_frame["price_ratio"],nan_policy="omit")
    different = None
    better = None
    if p_value < 0.01:
        different = True
    else:
        different = False
    if t_stat < 0:
        better = "university town"
    else:
        better = "non-university town"

    return (different, p_value, better)

