import requests
from dotenv import load_dotenv
import os

def get_saved_tracksID(param_session):
    """
    'param_session ={'app_secret':'1b2d32133792c353a555ff83c31ac6d8',
    'app_id':'521242',
    'access_token':DEEZER_TOKEN}
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

def request_json(operation,URL,param_session):
    session = requests.session()
    response = session.request(operation,URL,params=param_session)
    
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        return "Error: " + str(e)

    # Must have been a 200 status code
    if response.json() == True:
        return True
    elif response.json().get('error') : 
        if response.json()['error']['code'] == 801: # track already saved
            return response.json()
        else:
            print(response.json()['error']['message'])
    else:
        json_obj = response.json()
        return json_obj


def deezer_search(artist=None,track=None,album=None):
    #initiate parameters
    URL = 'https://api.deezer.com/search?q='
    load_dotenv()
    param_session = {'app_secret':os.environ['DEEZER_CLIENT_SECRET'],
                'app_id': os.environ['DEEZER_APP_ID'],
                'access_token':'frWCKCQyzmjnisjI1lmQRsjHrgMADK55FdosZx7J300AB7SRakC'#os.environ['DEEZER_TOKEN']
                }
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
        
def reformat_track_name (trackname):
    if 'feat.' in trackname or '(&'in trackname :
        index = trackname.find('(')
        newname = trackname[:index]
        return newname

def search_deezertracksID_from_spotify_library(df_library_spotify,index_to_ban=[]):
    """ Takes a Dataframe of Songs and give the Deezer trackID
        Input:  - dataframe with columns:'Artists', 'Tracks', 'Albums', 'TrackID'
                - Deezer client
        Return :    -Tracks_id: list of Track id 
                    -unmatched: list of soungs characteristics unmatched
                    -song_found_without_artist : int
    """
    # get deezer trackID from spotify library:
    Tracks_id = [] 
    unmatched=[]
    song_found_without_artist = 0
    df_library_spotify['Deezer_trackid'] = -1
    for index,row in df_library_spotify.iterrows():
        print(str(index))
        if index in index_to_ban : # exception due to format search futher
            unmatched.append([row.Artists,row.Tracks,row.Albums])
            print('unmatched\n')
        else:
            resultID = deezer_search(artist=row.Artists,track=reformat_track_name(row.Tracks),album=row.Albums)
            if resultID>-1:
                Tracks_id.append(resultID)
                #df_library_spotify['Deezer_trackid'][index] = resultID
                df_library_spotify.loc[index,'Deezer_trackid']=resultID
            else :
                resultID = deezer_search(artist=row.Artists,track=reformat_track_name(row.Tracks))
                if resultID>-1:
                    Tracks_id.append(resultID)
                    df_library_spotify.loc[index,'Deezer_trackid']=resultID
                else :
                    resultID = deezer_search(track=reformat_track_name(row.Tracks),album=row.Albums)
                    if resultID>-1:
                        Tracks_id.append(resultID)
                        df_library_spotify.loc[index,'Deezer_trackid']=resultID
                        song_found_without_artist += +1           
                    else:
                        unmatched.append([row.Artists,row.Tracks,row.Albums])
    return df_library_spotify,Tracks_id,unmatched,song_found_without_artist

def add_track_deezer(tracksID_already_saved,newtracks_id):
    URL = 'https://api.deezer.com/user/me/tracks'
    load_dotenv()
    param_session ={'app_secret':os.environ['DEEZER_CLIENT_SECRET'],
                    'app_id': os.environ['DEEZER_APP_ID'],
                    'access_token':'freCiD8xDNCM9M2Gv5jOJOqS9DKHwI85rRNCP6A1Oz7KrtijK8W'}#os.environ['DEEZER_TOKEN']}
    count_new_tracks = 0
    alreadyIN_track = 0

    #counter=0
    for track in newtracks_id :
        if track in tracksID_already_saved:
            alreadyIN_track += 1
        else:
            #add track
            param_session['track_id'] = track
            response = request_json('POST',URL,param_session)
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
    return count_new_tracks,alreadyIN_track,tracksID_already_saved