import Deezer_util,utils,Spotify_util # other script

#useful library
import pandas as pd

## LOAD ENVIRONMENT VARIABLES : 
from dotenv import load_dotenv
import os



def main (songs,playlists,albums):
    load_dotenv()
    param_session = {'app_secret':os.environ['DEEZER_CLIENT_SECRET'],
                'app_id': os.environ['DEEZER_APP_ID'],
                'access_token':os.environ['DEEZER_TOKEN']
                }
    
    if songs == 'y':
        #already saved tracks ID
        print('Get tracks already saved in Deezer')
        deezer_saved_tracksIDs = Deezer_util.get_saved_tracksID(param_session)
        # get spotify tracks 
        print('Get Spotify Library')
        spotify_tracks_library = Spotify_util.get_tracks_df()
        print('Find the ID in deezer of the Spotify tracks')
        spotify_tracks_library,Spotify_Tracks_id,unmatched,song_found_without_artist = Deezer_util.search_deezertracksID_from_spotify_library(spotify_tracks_library)
        # add track to the library
        print('Update the Deezer Library')
        count_tracksadded,count_tracks_alreadysaved,deezer_saved_tracksIDs = Deezer_util.add_track_deezer(deezer_saved_tracksIDs,Spotify_Tracks_id)


    # Artistes
if __name__ == "__main__":
    songs = input('Wanna get all favorites songs ? (y/n) :')
    #playlists = input('Wanna get favorites playlists ? (y/n) :')
    #albums = input('Wanna get favorites albums ? (y/n) :')
    main(songs,'n','n')
else: #useless
    print("main is being imported") 