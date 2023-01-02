from mastodon import Mastodon

class MastodonAccountManager():
    def __init__(self):
        self.instance =  Mastodon(client_id = 'hedonodon_clientcred.secret', access_token = 'hedonodon_usercred.secret')
