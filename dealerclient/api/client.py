import copy
import requests
import six

from dealerclient.api import app_tasks
from dealerclient.api import apps
from dealerclient.api import charts
from dealerclient.api import httpclient
from dealerclient.api import organizations
from dealerclient.api import projects
from dealerclient.api import sharedclusters
from dealerclient.api import workspaces
from dealerclient import exceptions


_DEFAULT_DEALER_URL = "https://go.kuberlab.io/api/v0.2"


class Client(object):
    def __init__(self, session=requests, **kwargs):
        # We get the session at this point, as some instances of session
        # objects might have mutexes that can't be deep-copied.
        req = copy.deepcopy(kwargs)
        dealer_url = req.get('dealer_url')

        if dealer_url and not isinstance(dealer_url, six.string_types):
            raise RuntimeError('Dealer url should be a string.')

        if not dealer_url:
            dealer_url = _DEFAULT_DEALER_URL

        http_client = httpclient.HTTPClient(
            dealer_url,
            session=session,
            **req
        )

        # Create all resource managers.

        self.workspaces = workspaces.WorkspaceManager(http_client)
        self.organizations = organizations.OrganizationManager(http_client)
        self.projects = projects.ProjectManager(http_client)
        self.apps = apps.AppManager(http_client)
        self.app_tasks = app_tasks.AppTaskManager(http_client)
        self.sharedclusters = sharedclusters.SharedClusterManager(http_client)
        self.charts = charts.ChartManager(http_client)


def create_session(base_url=_DEFAULT_DEALER_URL, **kwargs):
    """Creates a new session for cloud-dealer client.

    :param base_url: dealer base url.
    :param username: username
    :param password: password
    :param token: API token created via API
    :return: request.Session object.
    """
    username = kwargs.get('username')
    password = kwargs.get('password')
    token = kwargs.get('token')

    ses = requests.Session()
    if token:
        ses = requests.Session()
        ses.headers['Authorization'] = 'Bearer %s' % token
        return ses
    elif username and password:
        auth_url = '%s/auth/login' % base_url
        resp = ses.post(
            auth_url,
            json={'LoginOrEmail': username, 'Password': password},
            headers={'Content-Type': 'application/json'}
        )
        if resp.status_code != 200:
            raise exceptions.DealerClientException(
                'Invalid auth: %s.' % resp.content
            )
        return ses

    raise exceptions.DealerClientException(
        "Provide either token or username and password."
    )
