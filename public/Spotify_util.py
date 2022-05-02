import pandas as pd

import spotipy # spotify python library
from spotipy.oauth2 import SpotifyOAuth

def get_tracks_df(
    print_loading: bool = False
) -> pd.DataFrame :
    """ Get the favorites tracks of the User

    Args:
        print_loading (bool, optional): print the loading of every track. Defaults to False.

    Returns:
        pd.DataFrame: columns(Tracks, Artists, Albums,trackid) with all the favorite tracks of the user
    """
    scope = 'user-library-read'
    spotipy_user = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    results = spotipy_user.current_user_saved_tracks()
    totalTracks = results['total']
    tracklist = []
    artistlist = []
    albumlist = []
    trackid = []
    
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
    return pd.DataFrame({ 'Tracks' : tracklist,
                    'Artists' : artistlist,
                    'Albums' : albumlist,
                    'trackid' : trackid
                    })

def get_albums_df(
    print_loading: bool = False
) -> pd.DataFrame:
    """ Get all the favorites albums of the user

    Args:
        print_loading (bool, optional): print the loading of every Album. Defaults to False )->pd.DataFrame(.

    Returns:
        pd.DataFrame: columns(Artists(str), Albums(str)) with all the favorite albums of the user
                    if multiple artists on the albums then Artists = 'Artist1/Artist2.../ArtistN'
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

def get_playlists_info(
    print_loading: bool = False
):
    """ Get the playlists info of the user

    Args:
        print_loading (bool, optional): print every playlist info. Defaults to False.

    Returns:
        list: list of every playlist name of the user
        list: list of id corresponding to the playlists of the user
        spotipy: spotipy object used to interact with Spotify API
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

def tracks_from_playlistID(
    userconnection: spotipy,
    playlistID: int
): 
    """ Return all track informations for a playlist

    Args:
        userconnection (spotipy): spotipy object used to interact with Spotify API
        playlistID (int): ID of the playlist

    Returns:
        list: trackIDS of a playlist
        list: tracks of a playlist
        list: artist of a playlist
        list: albums of a playlist
        Return lists :'trackIDS','tracklist','artistlist','albumlist' for a given 'PlaylistID'
    """
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

def get_playlists_tracks(
    playlist_name: str,
    playlists_id: int,
    userconnection: spotipy,
    print_loading: bool = False
)-> pd.DataFrame:
    """ Get track for all the playlists

    Args:
        playlist_name(str): playlists name to get tracks from
        playlist_id(int): playlists ID to get tracks from
        userconnection(spotipy): spotipy object to interact with spotify API
        print_loading (bool, optional): print when searching for some playlist info. Defaults to False.


    Returns:
        pd.DataFrame(): playlist info ('PlaylistName','TrackID','Tracks','Artists','Albums')
    """
    
    df_playlist = pd.DataFrame(columns=['PlaylistName','TrackID','Tracks','Artists','Albums'])

    for i,val in enumerate(playlists_id):
        if print_loading:
            pl_name=playlist_name[i]
            print(f'Search songs in playlist "{pl_name}"')
        # add one playlist
        df = pd.DataFrame(columns=['PlaylistName','TrackID'])
        trackIDS,tracklist,artistlist,albumlist = tracks_from_playlistID(userconnection,val)
        df['TrackID'] = trackIDS
        df['Tracks'] = tracklist
        df['Artists'] = artistlist
        df['Albums'] = albumlist
        df['PlaylistName'] = playlist_name[i]

        df_playlist = pd.concat([df_playlist,df],ignore_index=True)
    return df_playlist
        
def wanna_saved(
    tipo: str,
    df: pd.DataFrame
):
    """Ask the user to save the dataframe 'df' with the name 'tipo'.xlsx """
    saved= input(f'Want to save {tipo} to a file ? (y/n) :')
    if saved == 'y':
        df.to_excel(f'Data/{tipo}_spot.xlsx',index=True)
        print(f'{tipo} saved to an excel file')

def get_choose_playlists(
    print_loading: bool = False
) -> pd.DataFrame:
    """ Let user choose which playlist to keep and download infos of selected playlists

    Args:
        print_loading (bool, optional): show playlist kept by the user and loading of them. Defaults to False.

    Returns:
        pd.DataFrame:  with columns(TrackID(str), Tracks(str),Artists(str), Albums(str),PlaylistName(str))
    """

    playlist_name, playlist_id, userconnection = get_playlists_info() 
    print('\n')
    print(playlist_name)
    print('\n')
    keep_playlists = input('Keep all playlists ? (y/n) :')

    if keep_playlists == 'y':
        print('keep every playlists')
    else : 
        for playlist,id in zip(list(playlist_name),list(playlist_id)):
            tokeep = input(f'Keep {playlist} ? (y/n) :')
            if tokeep !='y':
                playlist_name.remove(playlist)
                playlist_id.remove(id)
    print('\n')
    if print_loading:
        print(f'playlists to get tracks : {playlist_name}')
        print('\n')
    return get_playlists_tracks(playlist_name,playlist_id,userconnection,print_loading)