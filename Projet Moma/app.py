import pandas as pd
import streamlit as st
from random import randrange
from PIL import Image
import requests
from io import BytesIO
import numpy as np

        
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(45deg, #008CD6, #001F33);
}
</style>
""", unsafe_allow_html=True)

st.title("MoMa tinder experience")

if "i" not in st.session_state:
    st.session_state.i = 0

if "a_afficher" not in st.session_state:
    
    artworks = pd.read_csv("./Donnees/Artworks.csv")
    artworks = artworks[~artworks["OnView"].isna()]
    artworks = artworks[~artworks.ImageURL.isna()].reset_index(drop = True)
    
    artworks.OnView = artworks.OnView.str.replace('"',"")
    
    artworks.loc[(artworks['OnView'] == "MoMA, Floor 1") | (artworks['OnView'] == "MoMA, Floor 1, Art Lab") | (artworks['OnView'] == "MoMA, Floor 1, Sculpture Garden"), "Zone"] = "Sculpture Garden"
    artworks.loc[(artworks['OnView'] == "MoMA, Floor 1, 1 South"), "Zone"] = "Design Gallery"
    
    artworks.loc[(artworks['OnView'] == "MoMA, Floor 2") | ((artworks['OnView'] >= "MoMA, Floor 2, 201") & (artworks['OnView'] <= "MoMA, Floor 2, 211")), "Zone"] = "Contemporary Art, North and West Galleries"
    artworks.loc[((artworks['OnView'] >= "MoMA, Floor 2, 212") & (artworks['OnView'] <= "MoMA, Floor 2, 216")), "Zone"] = "Contemporary Art, Central Gallery"
    artworks.loc[(artworks['OnView'] == "MoMA, Floor 2, 2 South"), "Zone"] = "Contemporary Art, South Gallery"
    
    artworks.loc[(artworks['OnView'] == 'MoMA PS1, Third floor') | (artworks['OnView'] == "MoMA, Floor 3") | (artworks['OnView'] == "MoMA, Floor 3, 3 South"), "Zone"] = "Robert Frank Gallery"
    artworks.loc[(artworks['OnView'] == "MoMA, Floor 3, 3 East"), "Zone"] = "American Late 20th Century Art Gallery"
    
    artworks.loc[(artworks['OnView'] == "MoMA, Floor 4") | ((artworks['OnView'] >= "MoMA, Floor 4, 400") & (artworks['OnView'] <= "MoMA, Floor 4, 407")), "Zone"] = "Mid-20th Century Art, North Gallery"
    artworks.loc[((artworks['OnView'] >= "MoMA, Floor 4, 408") & (artworks['OnView'] <= "MoMA, Floor 4, 413")), "Zone"] = "Mid-20th Century Art, West Gallery"
    artworks.loc[((artworks['OnView'] >= "MoMA, Floor 4, 414") & (artworks['OnView'] <= "MoMA, Floor 4, 421")), "Zone"] = "Mid-20th Century Art, South Gallery"
    
    artworks.loc[((artworks['OnView'] >= "MoMA, Floor 5, 500") & (artworks['OnView'] <= "MoMA, Floor 5, 507")), "Zone"] = "Early Modern Art, European Gallery"
    artworks.loc[((artworks['OnView'] >= "MoMA, Floor 5, 508") & (artworks['OnView'] <= "MoMA, Floor 5, 516")), "Zone"] = "Early Modern Art, American Gallery"
    artworks.loc[(artworks['OnView'] == "MoMA, Floor 5") | ((artworks['OnView'] >= "MoMA, Floor 5, 517") & (artworks['OnView'] <= "MoMA, Floor 5, 523")), "Zone"] = "Early Modern Art, Graphic Arts Gallery"
    
    artworks.loc[artworks['OnView'] == "MoMA, Floor 6", "Zone"] = "Thomas Schütte Gallery"
    
    
    
    artworks.loc[(artworks['Zone'] == "Sculpture Garden"), "Groupe"] = "Sculpture Garden"
    artworks.loc[(artworks['Zone'] == "Design Gallery"), "Groupe"] = "Design"
    artworks.loc[(artworks['Zone'] == "Contemporary Art, North and West Galleries") | (artworks['Zone'] == "Contemporary Art, Central Gallery") | (artworks['Zone'] == "Contemporary Art, South Gallery"), "Groupe"] = "Contemporary Art"
    artworks.loc[(artworks['Zone'] == "Mid-20th Century Art, North Gallery") | (artworks['Zone'] == "Mid-20th Century Art, West Gallery") | (artworks['Zone'] == "Mid-20th Century Art, South Gallery"), "Groupe"] = "Mid-20th Century Art"
    artworks.loc[(artworks['Zone'] == "Early Modern Art, European Gallery") | (artworks['Zone'] == "Early Modern Art, American Gallery") | (artworks['Zone'] == "Early Modern Art, Graphic Arts Gallery"), "Groupe"] = "Early Modern Art"
    artworks.loc[(artworks['Zone'] == "Thomas Schütte Gallery"), "Groupe"] = "Thomas Schütte"
    artworks.loc[(artworks['Zone'] == "Robert Frank Gallery"), "Groupe"] = "Robert Frank"
    artworks.loc[(artworks['Zone'] == "American Late 20th Century Art Gallery") , "Groupe"] = "American Late 20th Century Art"
    
    
    
    resampled_artworks = artworks.groupby("Zone").sample(n=185, replace=True)
    resampled_artworks = resampled_artworks.reset_index(drop=True)
    
    a_afficher = pd.DataFrame(columns = resampled_artworks.columns)
    
    st.session_state.likes = pd.DataFrame(columns = resampled_artworks.columns)
    st.session_state.dislikes = pd.DataFrame(columns = resampled_artworks.columns)
    
    
    for groupe in set(resampled_artworks["Groupe"]):
        
        for _ in range(2) :
            
            object_id = np.random.choice(resampled_artworks[resampled_artworks["Groupe"] == groupe].ObjectID, size = 1)[0]
            a_afficher = pd.concat([a_afficher, resampled_artworks[resampled_artworks["ObjectID"] == object_id].drop_duplicates()])
            resampled_artworks = resampled_artworks[resampled_artworks["ObjectID"] != object_id]
    
    for _ in range(9):
        object_id = np.random.choice(resampled_artworks.ObjectID, size = 1)[0]
        a_afficher = pd.concat([a_afficher, resampled_artworks[resampled_artworks["ObjectID"] == object_id].drop_duplicates()])
        resampled_artworks = resampled_artworks[resampled_artworks["ObjectID"] != object_id] 

    
    a_afficher = a_afficher.reset_index(drop = True)

    st.session_state.a_afficher = a_afficher


col1, col2, col3 = st.columns(3)

if st.session_state.i<25 :
    image_url = st.session_state.a_afficher["ImageURL"][st.session_state.i]
    
    
    
    st.markdown("""
    <style>
    /* LIKE */
    .st-key-like .stButton button {
        background-color: white;
        border-radius: 50%;
        width: 70px;
        height: 70px;
        font-size: 30px;
        color: white;
        border: 2px solid #5CB8FF;
    }
    .st-key-like .stButton button:hover {
        background-color: #5CB8FF;
    }
    
    /* DISLIKE */
    .st-key-dislike .stButton button {
        background-color: white;
        border-radius: 50%;
        width: 70px;
        height: 70px;
        font-size: 30px;
        color: black;
        border: 2px solid #FFB98A;
    }
    .st-key-dislike .stButton button:hover {
        background-color: #FFB98A;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title(st.session_state.i)
    
    
    with st.container(width = 600, height = 705, horizontal_alignment="center", key = "white_container"):
        #st.image(img, use_container_width=True)
        st.markdown("""
        <style>
        /* LIKE */
        .st-key-white_container {
        background-color: white;
        border: 5px solid #D3D3D3;
        }</style>
        """, unsafe_allow_html=True)
    
        with st.container(width = 500, height = 565, horizontal_alignment="center", key = "grey_container"):
            st.markdown("""
            <style>
            /* LIKE */
            .st-key-grey_container {
            background-color: #D3D3D3;
            }</style>
            """, unsafe_allow_html=True)
            headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.moma.org/"
            }
        
            response = requests.get(image_url, headers=headers)
        
            img = Image.open(BytesIO(response.content))
            img.thumbnail((500, 500))
            st.image(img)
        
    
        
            
        _, col1, _, _, col2,  _ = st.columns(6)
        # Boutons avec clés uniques
        with col1 :
            if st.button("❤️", key="like"):
                st.session_state.likes = pd.concat([st.session_state.likes, st.session_state.a_afficher.iloc[st.session_state.i]])
                st.session_state.i += 1
        
        with col2:
            if st.button("❌", key="dislike"):
                st.session_state.dislikes = pd.concat([st.session_state.dislikes, st.session_state.a_afficher.iloc[st.session_state.i]])
                st.session_state.i += 1
    
else : 
    st.title("Recommendations")
    recos_likes = (st.session_state.likes.groupby("Groupe").count()["Title"] / st.session_state.a_afficher.groupby("Groupe").count()["Title"]).head(3).index
    recos_dislikes = (st.session_state.dislikes.groupby("Groupe").count()["Title"] / st.session_state.a_afficher.groupby("Groupe").count()["Title"]).head(3).index

    st.title(f"{list(recos_likes)}")

# Pour l'image on va passer par PIL pour redimensionner puis st image ce sera plus facile




