import pandas as pd
import numpy as np
import re as regex


pd.set_option('display.max_columns', 20)
pd.set_option("display.width", 900)
pd.set_option('max_colwidth',40)
pd.set_option('display.max_rows', 1000)

energy_data_path = r"C:\Users\mosta\Desktop\Coursera - Data Science Track\Week 3\Energy Indicators.xls"
gdp_data_path = r"C:\Users\mosta\Desktop\Coursera - Data Science Track\Week 3\world_bank.csv"
jounrnal_data_path = r"C:\Users\mosta\Desktop\Coursera - Data Science Track\Week 3\scimagojr-3.xlsx"


def prepare_energy_dataset():
    #Load the data
    energy_frame =  pd.read_excel(energy_data_path, skiprows=17, usecols=range(2, 6), skipfooter=38)
    energy_frame.columns = ['Country', 'Energy Supply', 'Energy Supply per Capita', '% Renewable'] #set the columns names as requested
    energy_frame = energy_frame.replace('...', np.nan) #replace '...' with np.nan

    #handle countries that has paranthes and remove digits
    remove_paranthesRegex = r'\([^)]*\)'
    energy_frame["Country"] = energy_frame["Country"].apply(lambda x: regex.sub(remove_paranthesRegex,'', x).replace("  ", " ").strip())
    energy_frame["Country"] = energy_frame["Country"].apply(lambda x: ''.join([i for i in x if not i.isdigit()]))

    energy_frame["Energy Supply"] = energy_frame["Energy Supply"] * 1000000  #Convert to kilojoles

    # Hard countries names to be chnaged
    energy_frame = energy_frame.replace('Republic of Korea', 'South Korea')
    energy_frame = energy_frame.replace('United States of America', 'United States')
    energy_frame = energy_frame.replace('United Kingdom of Great Britain and Northern Ireland', 'United Kingdom')
    energy_frame = energy_frame.replace('China, Hong Kong Special Administrative Region', 'Hong Kong')
    return energy_frame

def prepare_gpb_dataset():
    gdp_frame = pd.read_csv(gdp_data_path, skiprows=4)
    gdp_frame.replace("Korea, Rep.", "South Korea",inplace=True)
    gdp_frame.replace("Iran, Islamic Rep.", "Iran", inplace=True)
    gdp_frame.replace("Hong Kong SAR, China", "Hong Kong", inplace= True)
    gdp_frame = gdp_frame.rename(columns={'Country Name': 'Country'})
    return gdp_frame

def prepare_journal_dataset():
    journal_frame = pd.read_excel(jounrnal_data_path)
    return journal_frame


#Initialize dataframes
energy = prepare_energy_dataset()
GDP = prepare_gpb_dataset()
ScimEn = prepare_journal_dataset()

def answer_one():
    #Join 3 datasets
    joined_frame = (energy.merge(GDP, left_on="Country", right_on="Country")
                    .merge(ScimEn, left_on="Country", right_on="Country"))

    # Change index to Countries as required
    joined_frame.set_index("Country", inplace=True)

    # Extract needed columns
    joined_frame = joined_frame[
        ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index',
         'Energy Supply', 'Energy Supply per Capita', '% Renewable', '2006', '2007', '2008', '2009', '2010', '2011',
         '2012', '2013', '2014', '2015']]

    # Get entries with rank from 1 to 15
    joined_frame = joined_frame[joined_frame["Rank"] <= 15]

    return joined_frame


def answer_two():
    joined_frame_outer = (GDP.merge(energy, left_on="Country", right_on="Country", how="outer")
                    .merge(ScimEn, left_on="Country",right_on="Country", how="outer"))
    joined_frame_inner  = (energy.merge(GDP,left_on="Country", right_on="Country")
                    .merge(ScimEn, left_on = "Country", right_on="Country"))

    return len(joined_frame_outer) - len(joined_frame_inner) #return number of rows lost



def answer_three():
    frame = answer_one()
    frame["AVG"] = frame[['2006', '2007', '2008', '2009', '2010', '2011',
         '2012', '2013', '2014', '2015']].mean(axis=1, skipna = True)
    avgGDP = frame["AVG"]
    return avgGDP


def answer_four():
    frame = answer_one()
    frame = frame[['2006', '2007', '2008', '2009', '2010', '2011',
                   '2012', '2013', '2014', '2015']]

    # caluclate average over the last 10 years
    frame["GDP average"] = frame.mean(axis=1)

    # Get the 6th largest average GDP
    frame.sort_values('GDP average', ascending=False, inplace=True)
    frame["GDP change"] = frame["2015"] - frame["2006"]
    return frame.iloc[5]["GDP change"]

def answer_five():
    frame = answer_one()
    return frame["Energy Supply per Capita"].mean()

def answer_six():
    ser = answer_one()["% Renewable"]
    return (ser.idxmax(), ser.max())

def answer_seven():
    frame = answer_one()
    frame["Citations Ratio"] = frame["Self-citations"] / frame["Citations"]

    return (frame["Citations Ratio"].idxmax(), frame["Citations Ratio"].max())

def answer_eight():
    frame = answer_one()
    frame["Population Estimate"] = frame["Energy Supply"] / frame["Energy Supply per Capita"]
    frame.sort_values('Population Estimate',ascending=False, inplace=True)
    return frame.iloc[2].name

def answer_nine():
    frame = answer_one()
    frame["Population Estimate"] = frame["Energy Supply"] / frame["Energy Supply per Capita"]
    frame["Documents per capita"] = frame["Citable documents"]/ frame["Population Estimate"]
    return frame['Documents per capita'].astype('float64').corr(frame['Energy Supply per Capita'].astype('float64'), method="pearson")

def answer_ten():
    frame = answer_one()
    renewable_median = frame["% Renewable"].median()
    frame["Is Above Median"] = frame["% Renewable"].apply(lambda x: 1 if x >= renewable_median else 0)
    frame.sort_values("Rank", ascending = True, inplace = True)
    HighRenew = frame["Is Above Median"]
    HighRenew.name = "HighRenew"
    return HighRenew


def answer_eleven():
    continent_dic = {'China':'Asia',
                  'United States':'North America',
                  'Japan':'Asia',
                  'United Kingdom':'Europe',
                  'Russian Federation':'Europe',
                  'Canada':'North America',
                  'Germany':'Europe',
                  'India':'Asia',
                  'France':'Europe',
                  'South Korea':'Asia',
                  'Italy':'Europe',
                  'Spain':'Europe',
                  'Iran':'Asia',
                  'Australia':'Australia',
                  'Brazil':'South America'}


    frame = answer_one()# Prepare dataframe
    frame["continent"] = pd.Series(continent_dic) # Append continents
    frame["Population Estimate"] = frame["Energy Supply"] / frame["Energy Supply per Capita"] # Prepare population estimate

    #BELOW CODE CRASHES AND A "KEY ERROR" EXCEPTION IS THROWN
    # Continent_pivot = pd.pivot_table(frame,
    #                                  index="continent",
    #                                  values="Population Estimate",
    #                                  aggfunc={"size": len, "sum": np.sum, "mean": np.mean, "std": np.std}
    #                                  )
    Continent_pivot = pd.pivot_table(frame,
                                     index="continent",
                                     values="Population Estimate",
                                     aggfunc=[len, np.sum,  np.mean, np.std ],
                                     )



    # Rename columns and index
    Continent_pivot.columns = ['size', 'sum', 'mean', "std"]
    Continent_pivot.index.name = "Continent"
    return Continent_pivot


def answer_twelve():
    continent_dic = {'China': 'Asia',
                     'United States': 'North America',
                     'Japan': 'Asia',
                     'United Kingdom': 'Europe',
                     'Russian Federation': 'Europe',
                     'Canada': 'North America',
                     'Germany': 'Europe',
                     'India': 'Asia',
                     'France': 'Europe',
                     'South Korea': 'Asia',
                     'Italy': 'Europe',
                     'Spain': 'Europe',
                     'Iran': 'Asia',
                     'Australia': 'Australia',
                     'Brazil': 'South America'}

    frame = answer_one()  # Prepare dataframe
    frame["continent"] = pd.Series(continent_dic)  # Append continents
    #frame["bins"] = pd.cut(frame["% Renewable"], 5)
    frame.reset_index(inplace=True)
    grouped = frame.groupby(["continent", pd.cut(frame['% Renewable'], 5)])['Country'].count()

    return grouped

def answer_thirteen():
    frame = answer_one()
    frame["Population Estimate"] = frame["Energy Supply"] / frame["Energy Supply per Capita"]
    frame["Population Estimate"] = frame["Population Estimate"].map('{:,}'.format)
    PopEst = frame["Population Estimate"]
    PopEst.name = "PopEst"
    return PopEst

