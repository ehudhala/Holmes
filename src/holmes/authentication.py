import bs4
import requests
from config import USERNAME, PASSWORD
from utils import create_logger, AuthenticationError

LOGIN_URL = 'http://www.holmesplace.co.il/user/login'
GIVAT_SHMUEL_CLUB_LESSONS_URL = 'http://www.holmesplace.co.il/clubs_services/club/56676/lessons'

logger = create_logger(__name__)


def authenticate(session, username=USERNAME, password=PASSWORD):
    """
    Gets a session, and authenticates it against the HolmesPlace website.
    To authenticate we first need to log in, and then send a request to a page found in an iframe in their site.
    (A dirty hack they did so that everyone entering their site goes to the iframe and authenticates)
    :param session: The session to authenticate.
    :param username: The username to authenticate with.
    :param password: The password to authenticate with.
    """
    session.post(LOGIN_URL, data={
        'name': username,
        'pass': password,
        'form_id': 'user_login'
    })
    logger.debug('POSTed the user and pass, the session cookies are set.')

    authenticate_against_asp(session)

    logger.debug('Sent a request to the iframe in the asp page, asp cookies are set.')


def authenticate_against_asp(session):
    """
    Since Holmes Place developers are dirty, we need to also send a request
    to the address embedded in an iframe in the page.
    In the address they give us a token,
    that when sent to the asp server generates a cookie for our ASP session.

    Sometimes in random, the iframe just isn't included in the page,
    so we check that it is, and try again if it isn't
    """
    for _ in xrange(10):
        lessons_page = session.get(GIVAT_SHMUEL_CLUB_LESSONS_URL).content
        lessons_page_soup = bs4.BeautifulSoup(lessons_page)
        # In their javascript they recognize their own iframe by its height.
        iframe_element = lessons_page_soup.find('iframe', {'height': 3000})
        if iframe_element is not None:
            return session.get(iframe_element['src'])
    raise AuthenticationError("couldn't authenticate to ASP. They never sent an iframe with a valid token.")


def create_session():
    """
    Creates an authenticated session for the HolmesPlace website.
    """
    session = requests.Session()
    logger.debug('Created session.')
    authenticate(session)
    logger.info('Authenticated session.')
    return session

