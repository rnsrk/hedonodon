from langdetect import detect
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

    def getLocalTimeline(self, minId=None):
        return self.mastodonInstance.timeline_local(min_id=minId, limit=500)

    def cleanhtml(self, raw_html):
        cleantext = re.sub(self.compilePattern, '', raw_html)
        cleantext = re.sub(r'http\S+', '', cleantext)
        return cleantext

    def buildTootsDataframe(self, minId=None):
        toots = []
        allTimelineResults = []
        timelinePagination = self.getLocalTimeline(minId)

        while timelinePagination:
            allTimelineResults = allTimelineResults + timelinePagination
            timelinePagination = self.mastodonInstance.fetch_previous(timelinePagination)
        for i in allTimelineResults:
            content = self.cleanhtml(i.content)
            language = detect(content)
            sentiment = self.sentiTooter.analyze(language, content)
            toot = {
                "sentiment": sentiment[0],
                "model": sentiment[1],
                "toot": content,
                "datetime": i.created_at.astimezone(self.localTimezone),
                "language": language,
                "userName": i.account.display_name,
                "userId": i.account.id,
                "tootId": i.id
            }
            toots.append(toot)
        toots.sort(key=lambda item:item.get('datetime'))
        return pd.DataFrame.from_records(toots)