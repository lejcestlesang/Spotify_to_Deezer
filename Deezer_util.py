from logging import raiseExceptions
import requests

import pandas as pd

import oauth_deezer

import os

def wanna_saved(
    tipo: str,
    df: pd.DataFrame
):
    """Ask the user to save the 'df' 

    Args:
        tipo (str): name used to saved the df
        df (pd.DataFrame): 
    """
    saved= input(f'Want to save {tipo} to a file ? (y/n) :')
    if saved == 'y':
        df.to_excel(f'Data/{tipo}_Deezer.xlsx')
        print(f'{tipo} from saved to an excel file')

def request_json(
    operation: str,
    URL: str,
    param_session: dict,
    print_json: bool = False
):
    """ request 'operation' to the Deezer API 

    Args:
        operation (str): type of operation
        URL (str): URL of Deezer API
        param_session (dict): parameters for the request(connection parameters + details of the request)
        print_json (bool, optional): print the json response of the request. Defaults to False.

    Raises:
        Exception: Request not Valid 

    Returns:
        True: request is valid and not need to respond
        False: resquest invalid for some reason
        dict: response of the request 
    """
    session = requests.session()
    response = session.request(operation,URL,params=param_session)

    if response.status_code == 200 :
        if print_json==True:
            print(response.json())

        if response.json() == True:
            return True
        elif response.json().get('error') : 
            if response.json()['error']['code'] == 801: # track already saved check if needed to return false as well
                return response.json()
            else:
                print(response.json()['error']['message'])
                return False
        else:
            json_obj = response.json()
            return json_obj
    else :
        raise Exception('Status code not equal to 200')

def get_saved_tracksID(
    param_session: dict
) -> list:
    """ return a list of 'tracksID_already_saved'

    Args:
        param_session (dict): parameters for the request(connection parameters + details of the request)

    Returns:
        list: list of int of trackID already saved in the Deezer library of the user
    """
    URL = 'https://api.deezer.com/user/me/tracks'
    session = requests.session()
    response = session.request("GET",URL,params=param_session)
    if response.json().get('error') : 
        print(response.json()['error']['message'])
    else:
        totaltracks = response.json()['total']
        tracksID_already_saved = []
        trackscounter = 0

        while totaltracks > len(tracksID_already_saved):
            for track in response.json()['data']:
                tracksID_already_saved.append(track['id'])
            trackscounter += len(response.json()['data'])
            if trackscounter < totaltracks:
                response = session.request("GET",url=response.json()['next'])
        return tracksID_already_saved

def get_playlists_info(
    param_session: dict,
    print_loading: bool = False
) -> dict:
    """ Get playlists infos of the users

    Args:
        param_session (dict): parameters for the request(connection parameters + details of the request)
        print_loading (bool, optional): print the names of the playlists of the Deezer User. Defaults to False.

    Returns:
        dict: playlist names as keys and playlist ID as value
    """

    URL = 'https://api.deezer.com/user/me/playlists'
    response = request_json('GET',URL,param_session)

    deezer_name_playlists_saved = [elem['title']for elem in response['data']]
    deezer_id_playlists_saved = [elem['id']for elem in response['data']]
    deezer_playlists = dict(zip(deezer_name_playlists_saved, deezer_id_playlists_saved))

    if print_loading:
        print(deezer_playlists.keys())

    return deezer_playlists

def deezer_search(
    param_session: dict,
    artist: str = None,
    track: str = None,
    album: str = None,
    print_json: bool = False,
    print_loading: bool = False
) -> int:
    """ Search the track ID in deezer of a song with the following parameters 

    Args:
        param_session (dict): parameters for the request(connection parameters + details of the request)
        artist (str, optional):  Defaults to None.
        track (str, optional):  Defaults to None.
        album (str, optional):  Defaults to None.
        print_json (bool, optional): print json response of the search Defaults to False.
        print_loading (bool, optional): print json loading of the search Defaults to False.

    Returns:
        int: TrackID in deezer API or -1 if not found
    """
    #initiate parameters
    URL = 'https://api.deezer.com/search?q='
    #launch request
    if artist : 
        URL = URL + (f'artist:"{artist}" ')
    if track : 
        URL = URL + (f'track:"{track}" ')
    if album : 
        URL = URL + (f'album:"{album}" ')
    
    if print_loading:
        print(URL)

    json_response = request_json('GET',URL,param_session,print_json)

    if json_response['total'] > 0 :
        return json_response['data'][0]['id']
    else: 
        return -1
        
def reformat_track_name (
    trackname: str
) -> str:
    """reformat the trackname

    Args:
        trackname (str): original trackname

    Returns:
        str: new trackname without the featuring informations
    """
    if 'feat.' in trackname or '(&'in trackname or '(with 'in trackname:
        index = trackname.find('(')
        newname = trackname[:index]
        return newname
    else:
        return trackname

def search_deezertracksID_from_spotify_library(
    param_session: dict,
    df_library_spotify: pd.DataFrame(),
    index_to_ban: list = [],
    print_loading: bool = False
):
    """ Find the corresponding trackID for each song in 'df_library_spotify'

    Args:
        param_session (dict): parameters for the request(connection parameters + details of the request)
        df_library_spotify (pd.DataFrame): with columns 'Tracks','Artists','Albums','trackid'(for spotify)
        index_to_ban (list, optional): index of the 'df_library_spotify' to ban in case of an error. Defaults to [].
        print_loading (bool, optional): Print if a song found a corresponding ID in deeer API. Defaults to False.

    Returns:
        pd.DataFrame(): df_library_spotify with a new column 'Deezer_trackid'
        list: TrackID (int) found in Deezer API
        int: number of trackID found without using the Artist name 
    """
    # get deezer trackID from spotify library:
    Tracks_id = [] 
    unmatched=[]
    song_found_without_artist = 0
    df_library_spotify['Deezer_trackid'] = -1
    for index,row in df_library_spotify.iterrows():
        found = False
        if index in index_to_ban : # exception due to format search futher
            unmatched.append([row.Artists,row.Tracks,row.Albums])
            print('unmatched\n')
        else:
            resultID = deezer_search(param_session,artist=row.Artists,track=reformat_track_name(row.Tracks),album=row.Albums)
            if resultID>-1:
                Tracks_id.append(resultID)
                #df_library_spotify['Deezer_trackid'][index] = resultID
                df_library_spotify.loc[index,'Deezer_trackid']=resultID
                found = True
            else :
                resultID = deezer_search(param_session,artist=row.Artists,track=reformat_track_name(row.Tracks))
                if resultID>-1:
                    Tracks_id.append(resultID)
                    df_library_spotify.loc[index,'Deezer_trackid']=resultID
                    found = True
                else :
                    resultID = deezer_search(param_session,track=reformat_track_name(row.Tracks),album=row.Albums)
                    if resultID>-1:
                        Tracks_id.append(resultID)
                        df_library_spotify.loc[index,'Deezer_trackid']=resultID
                        found = True
                        song_found_without_artist += +1           
        if print_loading:
            print(f'Songs : {row.Artists} : {row.Tracks} in {row.Albums} - found( {found} )')
    return df_library_spotify,Tracks_id,song_found_without_artist

def add_track_deezer(
    param_session: dict,
    newtracks_id: list,
    print_loading: bool = False,
    print_json: bool = False
):
    """ Add newtracks to User library

    Args:
        param_session (dict): parameters for the request(connection parameters + details of the request)
        newtracks_id (list): list of trackID(int) to add to the library
        print_loading (bool, optional): print number of track added and the number already saved. Defaults to False.
        print_json (bool, optional): print result of each request. Defaults to False.

    Returns:
        int: counter of new tracks
        int: counter of tracks already saved 
    """
    URL = 'https://api.deezer.com/user/me/tracks'
    count_new_tracks = 0
    alreadyIN_track = 0

    tracksID_already_saved = get_saved_tracksID(param_session)

    #counter=0
    for track in newtracks_id :
        if track in tracksID_already_saved:
            alreadyIN_track += 1
        else:
            #add track
            param_session['track_id'] = track
            response = request_json('POST',URL,param_session,print_json)
            if response == True : 
                #succesfully added
                count_new_tracks += 1
            elif response['error']['code']== 801:
                #alreadyIN
                alreadyIN_track += 1
                tracksID_already_saved.append(track)
            else :
                print(response)
                break
    if print_loading:
        print(f'{count_new_tracks} new tracks added, {alreadyIN_track} already saved')
    return count_new_tracks,alreadyIN_track

def add_playlists(
    df_spotify_playlists: pd.DataFrame(),
    param_session: dict,
    publicplaylist: bool = True,
    collaborative: bool = False,
    print_loading: bool = False,
    print_json: bool = False
):
    """ From 'df_spotify_playlists' add playlists and their tracks to the user library

    Args:
        df_spotify_playlists (pd.DataFrame): _description_
        param_session (dict): parameters for the request(connection parameters + details of the request)
        publicplaylist (bool, optional): parameter to set a new playlist as public or private. Defaults to True.
        collaborative (bool, optional): parameter to set a new playlist as collaborative or not. Defaults to False.
        print_loading (bool, optional): print some actions of the function. Defaults to False.
        print_json (bool, optional): print result of each request. Defaults to False.

    Return:
        pd.Dataframe: library updated on Deezer
    """

    URL = 'https://api.deezer.com/user/me/playlists'
    deezer_old_playlists = get_playlists_info(param_session,True)

    # for ech spotify playlist 
    for playlistname in df_spotify_playlists.PlaylistName.unique():
        # initiate counter to print
        new_trackcount,alreadyIN_trackcount = 0,0
        # get playlist dataframe
        df_playlist = df_spotify_playlists[df_spotify_playlists.PlaylistName == playlistname]
        #check if playlist alredy exist if not create a new one
        if playlistname not in deezer_old_playlists.keys():
            #set parameters
            param_session['title'] = playlistname
            param_session['public']=publicplaylist
            param_session['collaborative']=collaborative

            #create playlist
            session = requests.session()
            response = session.request("POST",URL,params=param_session)

            id_playlist = response.json()['id']
        else:
            id_playlist = deezer_old_playlists[playlistname]

        if print_loading:
            print(f'\nSearch Deezer trackID for all songs inside the Spotify playlist {playlistname} \n')
        # search for all the deezer track ID of the tracks inside spotify playlist
        df_library_spotify,Tracks_id,song_found_without_artist = search_deezertracksID_from_spotify_library(param_session,df_playlist,print_loading=print_loading)
        numbertracks = len(df_library_spotify)
        #add tracks to the playlist
        URL = f'https://api.deezer.com/playlist/{id_playlist}/tracks'
        param_session['playlist_id'] = id_playlist
        
        for song in Tracks_id:
            param_session['songs'] = [song]
            response = request_json('POST',URL,param_session)
            if response:
                new_trackcount += 1
            else : 
                alreadyIN_trackcount += 1
        if print_loading:
            print(f'In {playlistname} (in spotify {numbertracks} songs): {new_trackcount} new tracks added, {alreadyIN_trackcount} already saved \n')
    return df_library_spotify

# TO DO  add_albums & check error in playlists 

def add_albums(
    param_session: dict,
    spotify_albums: pd.DataFrame
):
    """ 'spotify_albums' Artists(str)/Albums(str)
    """
    # for every albums find the deezerid
    for index,row in spotify_albums.iterrows():
        param_session['id'] = deezer_search(param_session,artist=row.Artists,album=row.Albums)
        #upload the album
        URL = 'https://api.deezer.com/user/me/album'
        #TO finish

def Authentication(
    param_session: dict
):
    """ check if authentication works with current token, if not replace it with the new one

    Args:
        param_session (dict): connection parameters
    """

    if request_json('GET','https://api.deezer.com/user/me',param_session) == False:
        app_id = param_session['app_id']
        app_secret = param_session['app_secret']
        os.system(f"python oauth_deezer.py --app-id {app_id} --app-secret {app_secret}")

    # add option to delete the deezer token everytime a new one is generated
        