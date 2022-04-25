import pandas as pd

import spotipy # spotify python library
from spotipy.oauth2 import SpotifyOAuth

def get_tracks_df(print_loading=False):
    """add description --- 
    """
    scope = 'user-library-read'
    spotipy_user = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    results = spotipy_user.current_user_saved_tracks()
    totalTracks = results['total']
    tracklist = []
    artistlist = []
    albumlist = []
    trackid = []

    tracks_info = { 'tracklist' : tracklist,
                    'artistlist' : artistlist,
                    'albumlist' : albumlist,
                    'trackid' : trackid
                    }
    
    while len(tracklist)<totalTracks:
        for item in results['items']:
            track = item['track']
            if print_loading:
                print("%32.32s %s -id %s --album : %s" % (track['artists'][0]['name'], track['name'],track['id'],track['album']['name']))
            tracklist.append(track['name'])
            artistlist.append(track['artists'][0]['name'])
            albumlist.append(track['album']['name'])
            trackid.append(track['id'])
        results = spotipy_user.next(results) 
    return pd.DataFrame(tracks_info)

def get_albums_df(print_loading=False):
    """add description --- 
    """
    scope = 'user-library-read'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    results = sp.current_user_saved_albums()

    totalAlbums = results['total']
    artists = []
    albums = []

    while len(albums)<totalAlbums:
        for item in results['items']:
            albumname = item['album']['name']
            if len(item['album']['artists']) == 1 : 
                artistname = item['album']['artists'][0]['name']
            else :
                print(f' new PUTE for {albumname}')
                artistname = ""
                for i,val in enumerate(item['album']['artists']):
                    artistname = artistname+ val['name'] + '/'
            if print_loading:
                print(f'Album name : {albumname} by {artistname}')
            artists.append(artistname)
            albums.append(albumname)
        results = sp.next(results)

    return pd.DataFrame({
        'Artists': artists, 
        'Albums': albums,
        })



def get_playlists_names(print_loading=False):
    """Get the name of all the playlists of the user ---
    """
    # set connection
    scope = 'playlist-read-private'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    playlists = sp.current_user_playlists(limit=50)
    # if more than 50 playlists need to change the code above 

    # list of playlist name and their id
    playlist_name = []
    playlist_id = []
    for i, item in enumerate(playlists['items']):
        playlist_id.append(item['id'])
        playlist_name.append(item['name'])
        if print_loading:
            print("%d %s %s" % (i, item['name'], item['id']))
    return playlist_name,playlist_id, sp

def trackID_from_playlistID (userconnection,playlistID): 
    ''' Return a list of track ID for a given PlaylistID
    '''    
    pl_id = 'spotify:playlist:'+playlistID
    offset = 0
    trackIDS=[]
    tracklist = []
    artistlist = []
    albumlist = []
    while True:
        response = userconnection.playlist_items(pl_id,
                                    offset=offset,
                                    fields='items.track.id,items.track.album.name,items.track.name,items.track.artists.name,total',
                                    additional_types=['track'])
        
        if len(response['items']) == 0:
            break
        
        offset = offset + len(response['items'])

        for track in response['items']:
            trackIDS.append(track['track']['id'])
            tracklist.append(track['track']['name'])
            artistlist.append(track['track']['artists'][0]['name'])
            albumlist.append(track['track']['album']['name'])

    if response['total']==len(trackIDS):
        return trackIDS,tracklist,artistlist,albumlist
    else : 
        return None

def get_playlists_tracks(playlist_name,playlists_id,userconnection,print_loading=False):
    """Get the playlists of the user ---
    """
    df_playlist = pd.DataFrame(columns=['PlaylistName','TrackID','tracklist','artistlist','albumlist'])

    for i,val in enumerate(playlists_id):
        # add one playlist
        df = pd.DataFrame(columns=['PlaylistName','TrackID'])
        trackIDS,tracklist,artistlist,albumlist = trackID_from_playlistID(userconnection,val)
        df['TrackID'] = trackIDS
        df['tracklist'] = tracklist
        df['artistlist'] = artistlist
        df['albumlist'] = albumlist
        df['PlaylistName'] = playlist_name[i]

        df_playlist = pd.concat([df_playlist,df],ignore_index=True)
    return df_playlist

def get_playlists_tracks_version_dictionary(playlist_name,playlists_id,userconnection,print_loading=False):
    """Get the playlists of the user ---
    """
    results = pd.DataFrame()

    for i,val in enumerate(playlists_id):
        track_ID,track_list,artist_list,album_list = trackID_from_playlistID(val)
        playlist_info = { 'tracklist' : track_list,
                    'artistlist' : artist_list,
                    'albumlist' : album_list,
                    'trackid' : track_ID,
                    'playlistName' : playlist_name
                    }
        results = pd.concat([pd.DataFrame(playlist_info),results],ignore_index=True)
    return results   
        
def wanna_saved(tipo,df):
    """ASk the user to save the df """
    saved= input(f'Want to save {tipo} to a file ? (y/n) :')
    if saved == 'y':
        df.to_excel(f'{tipo}.xlsx')
        print(f'{tipo} from saved to an excel file')

    
if __name__ == "__main__": 
    print("spotifycode is being run directly")
else: 
    print("spotifycode is being imported")
