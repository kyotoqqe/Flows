import urllib.parse

def generate_spotify_oauth_redirect_uri():
    #create OauthConfig and bring constants into it
    query_params = {
        "client_id" : "01da06ec10a84823b6cbd8d7e8e8a4ae",
        "response_type": "code",
        "redirect_uri": "http://127.0.0.1:8000/api/auth/spotify/callback",
        "scope": " ".join([
            "user-read-email",
            "user-read-private"
        ])
        #state
    }

    query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
    base_url = "https://accounts.spotify.com/authorize?" + query_string
    return base_url