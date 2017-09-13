import urllib.request
import urllib.parse
import json
import sys
from urllib.error import HTTPError

print_verbose = False


def verbose_decorator(message):
    def function_wrapper(func):
        def decorated_function(*args, **kwargs):
            if print_verbose:
                print(message, end='', flush=True)
            return_value = func(*args, **kwargs)
            if print_verbose:
                print('done')
            return return_value

        return decorated_function

    return function_wrapper


# @verbose_decorator('Getting API key... ')
def get_api_key(path='tvdb_api_key.txt'):
    """Retrieves the TVDB API key.
    Returns the API key as a string.
    """
    return "F1ED0779FE210D1E"


@verbose_decorator('Requesting token... ')
def get_token(api_key=None):
    """Retrieves a JWT token for use in the current session after authenticating with the API key.
    Returns the token as a string.
    """
    if not api_key:
        api_key = get_api_key()
    url = 'https://api.thetvdb.com/login'
    data = {"apikey": api_key}
    encoded_data = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    token_data = get_tvdb_data(url, encoded_data, headers)
    token = token_data['token']
    return token


def get_tvdb_data(url, data, headers):
    """Performs a web request to the specified url with the specified data and headers.
    Returns the decoded json data response as a dict.
    """
    request = urllib.request.Request(url, data, headers)
    with urllib.request.urlopen(request) as response:
        json_byte_data = response.read()
    json_string_data = json_byte_data.decode('utf-8')
    json_data = json.loads(json_string_data)
    return json_data


@verbose_decorator('Retrieving series data... ')
def get_series_data(query, token=None):
    """Retrieves the data of all shows matching the query.
    Returns an empty list if no shows match.
    Returns the series data as a list.
    """
    if not token:
        token = get_token()
    base_url = 'https://api.thetvdb.com/search/series'
    encoded_query = urllib.parse.quote(query)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    url = '{}?name={}'.format(base_url, encoded_query)
    try:
        series_data = get_tvdb_data(url, None, headers)
        return series_data['data']
    except HTTPError:
        return []


def sort_format_episode(episode):
    """Formats the episode season and episode number as a string.
    For season 12 episode 136, it would return '0001200136'.
    This function assumes that there is no season or episode number > 99999.
    Returns the formatted season and episode number as a string.
    """
    season = episode['airedSeason']
    episode_number = episode['airedEpisodeNumber']
    return '{:0>5}{:0>5}'.format(season, episode_number)


def format_title(title):
    """Formats the title given to a usable file name.
    Strips some illegal characters out, and
    replaces some illegal characters with legal ones.
    Returns the formatted title as a string.
    """
    title = title.replace(':', ' -')  # replace colons with space-dash
    title = title.replace('?', '')  # remove question marks
    title = title.replace('$', '')  # remove dollar signs
    title = title.replace('/', '-')  # replace slash with dash
    title = title.replace('"', "'")  # replace double-quote with single-quote
    return title


@verbose_decorator('Retrieving episode list... ')
def get_episode_data(series_id, token=None):
    """Retrieves and sorts all of the episodes in the given season id.
    Returns the sorted episode data as a dict.
    """
    if not token:
        token = get_token()
    url = 'https://api.thetvdb.com/series/{}/episodes'.format(series_id)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    unsorted_episode_data = get_tvdb_data(url, None, headers)
    pages = unsorted_episode_data['links']['last']
    # If there are multiple pages of episodes, combine them all into unsorted_episode_data
    if pages > 1:
        for page in range(2, pages + 1):
            next_page_data = get_tvdb_data('{}?page={}'.format(url, page), None, headers)
            unsorted_episode_data['data'].extend(next_page_data['data'])
    # Sort the episodes
    episode_data = sorted(unsorted_episode_data['data'], key=sort_format_episode)
    return episode_data


@verbose_decorator('Formatting episode names... ')
def format_episode_names(episode_data,
                         name_template='[{season:0>{season_padding}}-{episode:0>{episode_padding}}] - {title}'):
    """Convert the episode data into a nicely formatted list of strings
    Returns the formatted episode names as a list of strings.
    """
    # Find out how much to pad the season and episode by finding the length of the longest season and episode number.
    season_padding = len(str(episode_data[-1]['airedSeason']))
    episode_padding = len(str(max(episode['airedEpisodeNumber'] for episode in episode_data)))
    name_list = []
    for episode in episode_data:
        season = episode['airedSeason']
        episode_number = episode['airedEpisodeNumber']
        title = format_title(episode['episodeName'])
        name = name_template.format(season_padding=season_padding, episode_padding=episode_padding,
                                    season=season, episode=episode_number, title=title)
        name_list.append(name)
    return name_list


def get_formatted_episode_names(series_id, token=None):
    """Retrieves the nicely formatted episode names of the show provided.
    Returns the nicely formatted episode names as a list of strings.
    """
    episode_data = get_episode_data(series_id, token)
    episode_names = format_episode_names(episode_data)
    return episode_names


def main():
    if len(sys.argv) >= 2:
        query = sys.argv[1]
    else:
        query = input("Search for a show > ")
        while not query:
            query = input("Search for a show > ")

    global print_verbose
    print_verbose = True

    token = get_token()
    series_data = get_series_data(query, token)
    if 'Error' in series_data:
        print('Error:\n', series_data['Error'])
        sys.exit()
    elif len(series_data) == 0:
        print('No shows matching that name found')
        sys.exit()
    elif len(series_data) == 1:
        series_id = series_data[0]['id']
    elif len(series_data) > 1:
        print('\nHere are all the shows that match that query:\n')
        for i in range(len(series_data)):
            print('{:>10} - {}'.format(i, series_data[i]['seriesName']))
        choice = input('\nChoose a show > ')
        while not choice.isdigit():
            choice = input('Choose a show > ')
        series_id = series_data[int(choice)]['id']

    episode_names = get_formatted_episode_names(series_id, token)
    print()
    print(*episode_names, sep='\n')


if __name__ == '__main__':
    main()
