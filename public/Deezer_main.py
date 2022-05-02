import Deezer_util,Spotify_util # other script

#useful library
import pandas as pd

## LOAD ENVIRONMENT VARIABLES : 
from dotenv import load_dotenv
import os



def main (songs,playlists,albums):
    # load connection parameters
    load_dotenv()
    param_session = {'app_secret':os.environ['DEEZER_CLIENT_SECRET'],
                'app_id': os.environ['DEEZER_APP_ID'],
                'access_token':os.environ['DEEZER_TOKEN']
                }
    
    Deezer_util.Authentication(param_session)
    
    if songs == 'y':
        # get spotify tracks 
        print('Get Spotify Library')
        spotify_tracks_library = Spotify_util.get_tracks_df()

        print('Find the ID in deezer of the Spotify tracks\n')
        spotify_tracks_library,Spotify_Tracks_id,song_found_without_artist = Deezer_util.search_deezertracksID_from_spotify_library(param_session,spotify_tracks_library)

        #print('Get tracks already saved in Deezer')
        #deezer_saved_tracksIDs = Deezer_util.get_saved_tracksID('tracks',param_session)

        print('Update the Deezer Library\n')
        Deezer_util.add_track_deezer(param_session,Spotify_Tracks_id,True)
    
    # load connection parameters
    if playlists == 'y':

        print('Get Spotify playlists\n')
        df_spotify_playlists = Spotify_util.get_choose_playlists(True)

        print('Add playlists to Deezer\n')
        df_playlist = Deezer_util.add_playlists(df_spotify_playlists,param_session,publicplaylist=False,collaborative=False,print_loading=True)
        Deezer_util.wanna_saved('deezer_playlists',df_playlist)

    if albums == 'y':
        print('Loading Spotify albums\n')
        df_spotify_albums = Spotify_util.get_albums_df()
        print('Uploading to Deezer\n')
        Deezer_util.add_albums(param_session,df_spotify_albums,True)

    # Artistes
if __name__ == "__main__":
    songs = input('Wanna get all favorites songs ? (y/n) :')
    playlists = input('Wanna get favorites playlists ? (y/n) :')
    albums = input('Wanna get favorites albums ? (y/n) :')
    main(songs,playlists,albums)
else: #useless
    print("main is being imported") 