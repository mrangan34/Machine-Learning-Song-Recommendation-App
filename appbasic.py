# import dependencies
from flask import Flask, request, jsonify, session, render_template, url_for, redirect
from flask_session import Session
import requests
import json
import time
import numpy as np
import pandas as pd
import csv
from bs4 import BeautifulSoup
from selenium import webdriver



app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

#next time, load model here

song_data1 = pd.read_csv('song_data.csv')
    

#txt file
song_data2 = pd.read_fwf('songdata_10000.txt')
song_data2.columns = ['user_id','song_id','listen_count']


# Unique Users
song_data2['user_id'].nunique()

filtered = song_data2[song_data2['listen_count'] > 15]

# merge datasets and remove duplicates
song_df = pd.merge(filtered, song_data1.drop_duplicates(['song_id']), on= "song_id", how='left')

combined_songs_df = song_df.dropna(axis = 0, subset = ['title'])
combined_songs_df

# Create pivot table
song_features_df = combined_songs_df.pivot_table(index=['title','artist_name'], columns = 'user_id', values = 'listen_count').fillna(0)
song_features_df_index = song_features_df.reset_index()

@app.route("/", methods=["POST", "GET"])
def hello():
    if request.method == "POST":
        song = request.form["sng"]
        session['song'] = song
        return redirect(url_for("song", sng=song))

    else:
        return render_template("search.html")

@app.route("/nomatch", methods=["POST", "GET"])
def nomatch():
    if request.method == "POST":
        song = request.form["sng"]
        session['song'] = song
        return redirect(url_for("song", sng=song))

    else:
        return render_template("index_after_no_match.html")


@app.route("/match", methods=["POST", "GET"])
def match():
    if request.method == "POST":
        song = request.form["sng"]
        session['song'] = song
        return redirect(url_for("song", sng=song))

    else:
        suggestion1 = session.get('suggestion1')
        suggestion2 = session.get('suggestion2')
        suggestion3 = session.get('suggestion3')
        suggestion4 = session.get('suggestion4')
        suggestion5 = session.get('suggestion5')
        track_list_0 = session.get('track_list_0')
        track_list_1 = session.get('track_list_1')
        track_list_2 = session.get('track_list_2')
        track_list_3 = session.get('track_list_3')
        track_list_4 = session.get('track_list_4')

        # print("testing line 59")
        # print(track_list_0)
        track_list = session.get('track_list')

        if len(track_list) == 5:
            return render_template("search_after_success.html", track_list_0 = track_list_0, track_list_1 = track_list_1, track_list_2 = track_list_2, track_list_3 = track_list_3, track_list_4 = track_list_4 )

        if len(track_list) == 4:
            return render_template("search_after_success.html", track_list_0 = track_list_0, track_list_1 = track_list_1, track_list_2 = track_list_2, track_list_3 = track_list_3 )

        if len(track_list) == 3:
            return render_template("search_after_success.html", track_list_0 = track_list_0, track_list_1 = track_list_1, track_list_2 = track_list_2 )

        if len(track_list) == 2:
            return render_template("search_after_success.html", track_list_0 = track_list_0, track_list_1 = track_list_1 )

        if len(track_list) == 1:
            return render_template("search_after_success.html", track_list_0 = track_list_0 )



@app.route("/<sng>", methods=["POST", "GET"])
def song(sng):

   
    song_title = session.get('song')

    if (song_features_df_index['title']==song_title).any():
        index_list = song_features_df_index.index[song_features_df_index['title'] == song_title].tolist()

        for i in index_list: 
            index_int = i
        
      
        from scipy.sparse import csr_matrix

        song_features_df_matrix = csr_matrix(song_features_df.values)

        from sklearn.neighbors import NearestNeighbors

        model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
        model_knn.fit(song_features_df_matrix)

        query_index = index_int
    
        distances, indices = model_knn.kneighbors(song_features_df.iloc[query_index,:].values.reshape(1, -1), n_neighbors = 6)

        song_list = []

        for i in range(0, len(distances.flatten())):

            if i == 0:
                print('Recommendations for {0}:\n'.format(song_features_df.index[query_index]))

            else:
                song_output = ('{1}'.format(i, song_features_df.index[indices.flatten()[i]], distances.flatten()[i]))
                song_output = str(song_output)
                song_list.append(song_output)
           
       

    
      
        suggestion1 = song_list[0]
        suggestion2 = song_list[1]
        suggestion3 = song_list[2]
        suggestion4 = song_list[3]
        suggestion5 = song_list[4]

        session['suggestion1'] = suggestion1
        session['suggestion2'] = suggestion2
        session['suggestion3'] = suggestion3
        session['suggestion4'] = suggestion4
        session['suggestion5'] = suggestion5
            
        i = 0
        song_search_url_list = []

        for song in song_list:
            song_name = f'song_list_{i}'
            

            song_search_url = str(song_list[i]).replace(",", "")
            song_search_url = song_search_url.replace(" (Album Version)", "")
            
            song_search_url = song_search_url.replace("  ", " ")
            song_search_url = song_search_url.replace(" ", "+")
            song_search_url = song_search_url.replace("'", "")
            song_search_url = song_search_url.replace("(", "")
            song_search_url = song_search_url.replace(")", "")
            
            song_search_url = 'https://www.google.com/search?q=spotify'+'+'+song_search_url

            song_search_url_list.append(song_search_url)
            i=i+1

        stripped_list = []

        for song_search_url in song_search_url_list:
            open_spotify_url_list = []
            r = requests.get(song_search_url)
            print(song_search_url)
            html = r.text
            soup = BeautifulSoup(html, "html.parser")


            results = soup.findAll('a')

            url_list = []
            print("all urls found on the google search page")
            print(url_list)

            for link in results:
                substring = 'https://open.spotify.com/track/'
                
                link = str(link)
                if substring in link:
                    print("OPEN.SPOTIFY URL FOUND")
                    url_list.append(link)
                else:
                    print("nay")

            if len(url_list)>0:
                first_link = url_list[0]
                first_link = first_link.split("&")[0]
                first_link = first_link.split("q=")[1]
                stripped_list.append(first_link)
                print(stripped_list)
        


        

       

        track_list = []

        for link in stripped_list:
            i = 0
            song_name = F"song_number{i}"
            song_name = link.split('.com/')[1]
            track_list.append(song_name)
            i = i+1
            
        if len(track_list)==5:    
            track_list[0]
            session['track_list_0'] = track_list[0]
            session['track_list_1'] = track_list[1]
            session['track_list_2'] = track_list[2]
            session['track_list_3'] = track_list[3]
            session['track_list_4'] = track_list[4]

        if len(track_list)==4:  
            track_list[0]
            session['track_list_0'] = track_list[0]
            session['track_list_1'] = track_list[1]
            session['track_list_2'] = track_list[2]
            session['track_list_3'] = track_list[3]  

        if len(track_list)==3:    
            track_list[0]
            session['track_list_0'] = track_list[0]
            session['track_list_1'] = track_list[1]
            session['track_list_2'] = track_list[2]

        if len(track_list)==2: 
            track_list[0]
            session['track_list_0'] = track_list[0]
            session['track_list_1'] = track_list[1]

        if len(track_list)==1: 
            session['track_list_0'] = track_list[0]   

        session['track_list'] = track_list 
        
  
        return redirect('/match')
   
      

    else:
        return redirect('/nomatch')


    
  



if __name__ == "__main__":
    app.run(debug=True)