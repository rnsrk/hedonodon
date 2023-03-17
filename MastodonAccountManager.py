from mastodon import Mastodon

class MastodonAccountManager():
    """Initialize the Mastodon account.
    """
    def __init__(self):
        self.instance = Mastodon(client_id = 'hedonodon_clientcred.secret', access_token = 'hedonodon_usercred.secret')
