import requests

import pandas as pd

def request_json(
    operation: str,
    URL: str,
    param_session: dict,
    print_json: bool =False
):
    """ request the 'operation' to be done at the 'URL' using 'param_session', 'print_json' can be use to print the results 
        return :    - 'json_obj' a dictionary
                    - True if the 'request' does not need to respond a json object
                    - False if their if there is an Error
    """
    session = requests.session()
    response = session.request(operation,URL,params=param_session)
    
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        return "Error: " + str(e)

    if print_json:
        print(response.json())
        print(response)

    # Must have been a 200 status code
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

def get_saved_tracksID(
    param_session: dict
):
    """ return a list of 'tracksID_already_saved'"""
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
    print_loading: Boolean=False
):
    """ Use 'param_session' to 
        return : a dictionary 'deezer_playlist' with playlists name as keys and playlists ID as value 
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
    album: str = None
):
    """ return the trackID (str) after searching for a 'track' from 'artist' on the 'album' 
                or -1 if it was not found
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

    json_response = request_json('GET',URL,param_session)

    if json_response['total'] > 0 :
        return json_response['data'][0]['id']
    else: 
        return -1
        
def reformat_track_name (
    trackname: str
):
    """ Return an newname (str) without informations of Featurings from a 'trackname'"""
    if 'feat.' in trackname or '(&'in trackname :
        index = trackname.find('(')
        newname = trackname[:index]
        return newname

def search_deezertracksID_from_spotify_library(
    param_session: dict,
    df_library_spotify: pd.DataFrame(),
    index_to_ban: list = [],
    print_loading: Boolean = False
):
    """ From 'df_library_spotify' with columns 'Artists', 'Tracks', 'Albums', 'TrackID'
        Return :    -'df_library_spotify' with the column 'Deezer_trackid' (int)
                    -'Tracks_id': list of int corresponding to the Track id of each song 
                    -'unmatched': list of songs unmatched
                    -'song_found_without_artist' : int
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
                    else:
                        unmatched.append([row.Artists,row.Tracks,row.Albums])
        if print_loading:
            print(f'Songs : {row.Artists} : {row.Tracks} in {row.Albums} - found( {found} )')
    return df_library_spotify,Tracks_id,unmatched,song_found_without_artist

def add_track_deezer(
    param_session: dict,
    newtracks_id: list,# list of int
    print_loading: Boolean = False,
    print_json: Boolean = True
):
    """ Add 'newtracks_id's to the user library 
        Return the number of 'count_new_tracks' and the number 'alreadyIN_track' 
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
    publicplaylist: Boolean = True,
    collaborative: Boolean = False,
    print_loading: Boolean = False,
    print_json: Boolean = False
):
    """From 'df_spotify_playlists' add playlists and their tracks to the user library"""

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
            print(f'Search Deezer trackID for all songs inside the SPotify playlist {playlistname}\n')
        # search for all the deezer track ID of the tracks inside spotify playlist
        df_library_spotify,Tracks_id,unmatched,song_found_without_artist = search_deezertracksID_from_spotify_library(param_session,df_playlist,print_loading=print_loading)

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
                print(df_library_spotify[df_library_spotify.Deezer_trackid == song])

        if print_loading:
            print(f'In {playlistname} : {new_trackcount} new tracks added, {alreadyIN_trackcount} already saved \n')
