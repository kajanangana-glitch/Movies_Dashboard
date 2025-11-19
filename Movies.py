#!/usr/bin/env python
# coding: utf-8

# In[1]:


# movie_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------- CONFIG ---------------------
st.set_page_config(page_title="Best Movies to Watch", layout="wide")
st.title("What Should I Watch Tonight?")


# In[2]:


df=pd.read_csv("netflix_data.csv")
df=df[df["Series or Movie"]=="Movie"]


# In[3]:


def runtime_to_min(x):
        if '< 30' in str(x): return 25
        if '30-60' in str(x): return 45
        if '1-2 hour' in str(x): return 90
        if '> 2 hrs' in str(x): return 150
        return 90
df['Minutes'] = df['Runtime'].apply(runtime_to_min)


# In[4]:


df["Boxoffice"] = df["Boxoffice"].str.replace(r"[^0-9.]", "", regex=True)



df["Boxoffice"] = pd.to_numeric(df["Boxoffice"], errors="coerce")


# In[5]:


df['Genre_List'] = df['Genre'].fillna('').str.split(', ')
df['Languages_List'] = df['Languages'].fillna('').str.split(', ')


# In[6]:


st.sidebar.header("Your Mood")
min_imdb = st.sidebar.slider("Minimum IMDb Score", 1.0, 10.0, 7.0, 0.1)
max_time = st.sidebar.slider("Max Runtime", 30, 180, 120, 10)
min_boxoffice=st.sidebar.slider("Min BoxOffice", 0, 2000000000, 50000000, 1)
selected_genres = st.sidebar.multiselect("Genre (optional)", 
    ['Action', 'Comedy', 'Drama', 'Romance', 'Horror', 'Thriller', 'Sci-Fi', 'Animation', 'Documentary'])
selected_languages = st.sidebar.multiselect("Language (optional)", 
    ['English', 'Spanish', 'French', 'Hindi', 'Tamil', 'Mandarin', 'Korean', 'Japanese'])


# In[7]:


# Apply filters
filtered = df[df['IMDb Score'] >= min_imdb]
filtered = filtered[filtered['Minutes'] <= max_time]
filtered = filtered[filtered['Boxoffice'] >= min_boxoffice]
if selected_genres:
    filtered = filtered[filtered['Genre_List'].apply(lambda x: any(g in selected_genres for g in x))]
if selected_languages:
    filtered = filtered[filtered['Languages_List'].apply(lambda x: any(g in selected_languages for g in x))]


# In[8]:


c1, c2= st.columns(2)
with c1: st.metric("Movies Found", len(filtered))
with c2: st.metric("Highest IMDb", f"{filtered['IMDb Score'].max():.1f} stars")


# In[9]:


st.markdown("### High Rating + Critics Love It")
fig = px.scatter(
    filtered,
    x="IMDb Score",
    y="Metacritic Score",
    color="Boxoffice",
    hover_name="Title",
    hover_data=[ "Genre", "Minutes", "Boxoffice"],
    color_continuous_scale="Plasma",
    size_max=70,
    labels={"IMDb Score": "IMDb Rating"},
    title="Sweet Spot: Loved by Fans AND Critics"
)
fig.add_hline(y=70, line_dash="dash", line_color="white", annotation_text="Audience Hit")
fig.add_vline(x=7.5, line_dash="dash", line_color="white", annotation_text="Critics Love")
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)


# In[10]:


st.markdown("### Your Top 10 Popular Picks")
top10 = filtered.nlargest(10, 'IMDb Score')[['Title', 'Release Date', 'IMDb Score', 'Rotten Tomatoes Score', 'Metacritic Score', 'Runtime', 'Boxoffice']]
top10 = top10.round(1)
top10.index = range(1, len(top10)+1)
st.dataframe(top10.style.background_gradient(cmap='RdYlGn'), use_container_width=True)


# In[11]:


# SURPRISE ME – USES YOUR FILTERS AUTOMATICALLY
st.markdown("### Surprise Me!")
if st.button("Pick a movie for me!", use_container_width=True):


    if len(filtered) == 0:
        st.warning("No movie has a poster with your current filters 😢\nTry lowering IMDb or increasing time.")
    else:
        movie = filtered.sample(1).iloc[0]


        st.markdown(f"### {movie['Title']}")
        st.write(movie['Summary'])
        st.balloons()

