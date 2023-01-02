import pytz
import pandas as pd
import re
from SentiTooter import SentiTooter
from pprint import pprint


class TootCrawler():

    def __init__(self, mastodonInstance) -> None:
        self.mastodonInstance = mastodonInstance
        self.compilePattern = re.compile('<.*?>')
        self.sentiTooter = SentiTooter()
        self.localTimezone = pytz.timezone('Europe/Berlin')

    def getLocalTimeline(self,  sinceId=None):
        return  self.mastodonInstance.timeline_local(since_id=sinceId)

    def cleanhtml(self, raw_html):
        cleantext = re.sub(self.compilePattern, '', raw_html)
        cleantext = re.sub(r'http\S+', '', cleantext)
        return cleantext

    def buildTootsDataframe(self, sinceId=None):
        toots = []

        for i in self.getLocalTimeline(sinceId):
            content = self.cleanhtml(i.content)
            sentiment = self.sentiTooter.analyze(i)
            toots.append(
                    {
                            "sentiment": sentiment[0],
                            "compound": sentiment[1],
                            "userName": i.account.display_name,
                            "userId": i.account.id,
                            "toot": content,
                            "datetime": i.created_at.astimezone(self.localTimezone),
                            "language": i.language,
                            "tootId": i.id
                    }
                )
        toots.sort(key=lambda item:item.get('datetime'))
        return pd.DataFrame.from_records(toots)