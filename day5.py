from hello import barChart
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from wordcloud import WordCloud
import plotly.express as px
from Adding_Data import db_execute_fetch




#st.set_page_config(page_title="Topic Analysis and Sentiment Analysis", layout="wide")

def loadData():
    query = "select * from Twitter"
    df = db_execute_fetch(query, dbName="tweets", rdf=True)
    return df


def select_original_author():
    df = loadData()
    Author= st.sidebar.multiselect("Choose an Author", list(df['original_author'].unique()))
    if Author:
        df = df[np.isin(df, Author).any(axis=1)]
        st.write(df)
        
        
def selectLocAndPola():
    df = loadData()
    df['score'] = df['polarity'].apply(text_category) 
    location = st.sidebar.multiselect("choose Location of tweets", list(df['place'].unique()))
    Polarity = st.sidebar.multiselect("choose Polarity of tweets", list(df['score']))

    if location and not Polarity:
        df = df[np.isin(df, location).any(axis=1)]
        st.write(df)
    elif Polarity and not location:
        df = df[np.isin(df, Polarity).any(axis=1)]
        st.write(df)
    elif Polarity and location:
        location.extend(Polarity)
        df = df[np.isin(df, location).any(axis=1)]
        st.write(df)
    else:
        st.write(df)
        
  
        
        
def wordCloud():
    df = loadData()
    cleanText = ''
    for text in df['original_text']:
        tokens = str(text).lower().split()

        cleanText += " ".join(tokens) + " "

    wc = WordCloud(width=650, height=450, background_color='lightpink', min_font_size=5).generate(cleanText)
    st.title("Tweet Text Word Cloud")
    st.image(wc.to_array())   
    
    
def text_category(p):
    """
    A function  that takes a value p and returns, depending on the value of p, 
    a string 'positive', 'negative' or 'neutral'
    """
    if p > 0 : return 'positive'
    elif p == 0: return 'neutral'
    return 'negative'

# Count the number of positive, neutral, and negative
def polarity_count():
    df = loadData()
    df['score'] = df['polarity'].apply(text_category) 
    x= list(df['score'])
    return { 'positive': x.count('positive'), 'neutral': x.count('neutral'),
                            'negative': x.count('negative')  } 

    
    
def PolarityBarChart():
   
    st.title('Polarity BarChart')
    pol=polarity_count()
    pol_data= pd.DataFrame({
        'labels':list(pol.keys()), 
        'data':list(pol.values())})
    Bchart=px.bar(pol_data,x='labels', y='data')
    st.plotly_chart(Bchart)
    

def  Original_AuthPie():
    
    df = loadData()
    dfAuthCount = pd.DataFrame({'Tweet_count': df.groupby(['original_author'])['original_text'].count()}).reset_index()
    dfAuthCount[""] = dfAuthCount["original_author"].astype(str)
    dfAuthCount = dfAuthCount.sort_values("Tweet_count", ascending=False)
    dfAuthCount.loc[dfAuthCount['Tweet_count'] < 10, 'original_author'] = 'Other Authors'
    st.title(" Tweets Author pie chart")
    fig = px.pie(dfAuthCount, values='Tweet_count', names='original_author', width=500, height=350)
    fig.update_traces(textposition='inside', textinfo='percent+label')

    colB1, colB2 = st.beta_columns([2.5, 1])

    with colB1:
        st.plotly_chart(fig)
    with colB2:
        st.write(dfAuthCount)       
        
        
        
        
st.title("Data Display")
select_original_author()
selectLocAndPola()

st.title("Data Visualizations")
wordCloud()
with st.beta_expander("Show More Graphs"):
    PolarityBarChart()
    Original_AuthPie()