import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import pytz

if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

#set up PST
pst = pytz.timezone('America/Los_Angeles')

# initialize df of fters and sns -> can pull this from snowflake
fters = pd.read_csv("./allocation.csv")

#import dataset csv (this can be deleted after snowflake integration)
mc_data = pd.read_csv("./ft_mc_dataset.csv")

## I N T E R F A C E ##
st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="expanded", menu_items=None)

with st.sidebar:

    st.header("Souped-up Field Trial (Elm)")
    st.subheader("Daily Moisture Content Readings")
    st.write(date.today().strftime("%B %d, %Y"))
    
    #select from field trialers
    name = st.selectbox("Name", fters['Name'], None)        

    #input date sample was taken - make sure its pst
    sample_date = st.date_input("Sample Date: ", value=None)
    sample_time = st.time_input("Sample Time: ", time(9))        

    #input mc reading
    mc_reading = st.number_input("Moisture Content (%): ")

    #notes section
    notes = st.text_input("Notes (optional): ")

    submit = st.button("Submit")

    if submit:
        if name:
            new_mc = pd.DataFrame(columns=mc_data.columns)
            new_mc[['Name', 'SN']] = fters[fters['Name']==name]

            if sample_date and mc_reading:
                sample_datetime = pst.localize(datetime.combine(sample_date, sample_time))
                new_mc['Sample Date'] = sample_datetime
                read_date = datetime.now(pst)
                new_mc['Date Measured'] = read_date.replace(microsecond=0)
                new_mc['MC'] = mc_reading
                new_mc['Notes'] = notes

                #this part will change -> upload to snowflake
                mc_data = pd.concat([mc_data, new_mc], ignore_index=True)
                #update csv 
                mc_data.to_csv('ft_mc_dataset.csv', index=False)

            else:
                st.warning("Not all data has been entered",icon="⚠️")
            
        else:
            st.warning("Please select a name",icon="⚠️")

#display dataset/dataframe
st.dataframe(mc_data, use_container_width=True, hide_index=True)

