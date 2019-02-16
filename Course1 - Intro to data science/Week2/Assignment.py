import pandas as pd
import numpy as np

pd.set_option('display.max_columns',20)
desired_width = 500
pd.set_option('display.width', desired_width)


olympics_dv = pd.read_csv(r'C:\Users\mosta\Desktop\Coursera - Data Science Track\Week 2\Files\olympics.csv', index_col=0, skiprows=1)


for col in olympics_dv.columns:
    if col[:2]=='01':
        olympics_dv.rename(columns={col:'Gold'+col[4:]}, inplace=True)
    if col[:2]=='02':
        olympics_dv.rename(columns={col:'Silver'+col[4:]}, inplace=True)
    if col[:2]=='03':
        olympics_dv.rename(columns={col:'Bronze'+col[4:]}, inplace=True)
    if col[:1]=='№':
        olympics_dv.rename(columns={col:'#'+col[1:]}, inplace=True)

names_ids = olympics_dv.index.str.split('\s\(') # split the index by '('



olympics_dv.index = names_ids.str[0] # the [0] element is the country name (new index)
olympics_dv['ID'] = names_ids.str[1].str[:3] # the [1] element is the abbreviation or ID (take first 3 characters from that)

olympics_dv = olympics_dv.drop('Totals')


def answer_one():
    return olympics_dv[olympics_dv["Gold"] == olympics_dv["Gold"].max()].index[0]

#Which country had the biggest difference between their summer and winter gold medal counts?
def answer_two():
    #we use idxmax() to get the row index of max value for specified column
    olympics_dv["Diff"] = olympics_dv["Gold"] - olympics_dv["Gold.1"]
    return olympics_dv["Diff"].idxmax()

def answer_two2():
    global olympics_dv
    olympics_dv["Diff"] = (olympics_dv["Gold"] - olympics_dv["Gold.1"])
    mask = olympics_dv["Diff"] == olympics_dv["Diff"].max()
    olympics_dv = olympics_dv[mask]
    return olympics_dv.index[0]


def answer_three():
    olympics_dv_filtered = olympics_dv.copy()
    olympics_dv_filtered = olympics_dv_filtered[(olympics_dv_filtered["Gold"] >= 1) & (olympics_dv_filtered["Gold.1"] >= 1)]
    olympics_dv_filtered["Diff2"] = (olympics_dv_filtered["Gold"] - olympics_dv_filtered["Gold.1"]) / olympics_dv_filtered["Gold.2"]
    olympics_dv_result = olympics_dv_filtered[olympics_dv_filtered["Diff2"] ==olympics_dv_filtered["Diff2"].max() ]
    return olympics_dv_result.index[0]




def answer_four():
    points_series = (olympics_dv["Gold.2"] * 3) + (olympics_dv["Silver.2"] * 2) + (olympics_dv["Bronze"] * 1)
    return  points_series


census_df = pd.read_csv(r'C:\Users\mosta\Desktop\Coursera - Data Science Track\Week 2\Files\census.csv')


def answer_five():
    census_df_filtered = census_df[census_df["SUMLEV"] == 50]
    states_distinct = census_df_filtered["STNAME"].unique()

    state_County_dic = {}
    for state in states_distinct:
        county_count =len(census_df_filtered[census_df_filtered["STNAME"] == state])
        state_County_dic[state] = county_count

    my_df = pd.Series(state_County_dic)
    my_df = my_df.sort_values(ascending=False)
    return my_df.index[0]


#Only looking at the three most populous counties for each state,
#what are the three most populous states (in order of highest population to lowest population)? Use CENSUS2010POP.
#This function should return a list of string values.
def answer_six():
    census_filtered = census_df[census_df["SUMLEV"] == 50]
    unique_states = census_filtered["STNAME"].unique()

    agg_df = pd.DataFrame()
    agg_df["state"] = unique_states
    agg_df["sum_pop"] = 0
    agg_df.set_index("state",inplace=True)

    for state in unique_states:
        #get higher 3 counties for that state
        highest_3_counties_sum = census_filtered[census_filtered["STNAME"] == state].sort_values(by="CENSUS2010POP", ascending=False).iloc[:3]["CENSUS2010POP"].sum()
        agg_df.loc[state] = highest_3_counties_sum

    agg_df.sort_values(by="sum_pop",inplace=True,ascending=False)
    return list(agg_df.iloc[:3].index)


#Which county has had the largest absolute change in population within the period 2010-2015?
#(Hint: population values are stored in columns POPESTIMATE2010 through POPESTIMATE2015, you need to consider all six columns.)

#e.g. If County Population in the 5 year period is 100, 120, 80, 105, 100, 130, then its largest change in the period would be |130-80| = 50.

#This function should return a single string value.
def answer_seven():
    census_df_filtered = census_df[census_df["SUMLEV"] == 50].loc[:,
         ["STNAME","CTYNAME", "POPESTIMATE2010", "POPESTIMATE2011", "POPESTIMATE2012", "POPESTIMATE2013", "POPESTIMATE2014",
          "POPESTIMATE2015"]]

    census_df_filtered.set_index(["STNAME", "CTYNAME"], inplace = True)

    final_res = census_df_filtered.copy()
    final_res["dif"] = 0

    for index in census_df_filtered.index:
        diff = census_df_filtered.loc[index].max() - census_df_filtered.loc[index].min()
        final_res.loc[index, "dif"] = diff

    return final_res.sort_values(by="dif", ascending=False).head(10).index.get_level_values(1)[0]

#In this datafile, the United States is broken up into four regions using the "REGION" column.

#Create a query that finds the counties that belong to regions 1 or 2, whose name starts with
#'Washington', and whose POPESTIMATE2015 was greater than their POPESTIMATE 2014.

#This function should return a 5x2 DataFrame with the columns = ['STNAME', 'CTYNAME'] and the same index ID as the census_df (sorted ascending by index)


def answer_eight():
    census_df_filtered = census_df[(census_df["SUMLEV"] == 50) &
                                   ((census_df["REGION"] == 1) |
                                   (census_df["REGION"] == 2))
                                   & (census_df["CTYNAME"].str.startswith("Washington"))
                                    & (census_df["POPESTIMATE2015"] > census_df["POPESTIMATE2014"])
                                   ]

    return census_df_filtered.loc[:,['STNAME', 'CTYNAME']]





