from langdetect import detect
import pytz
import pandas as pd
from pandas import DataFrame
import re
from SentiTooter import SentiTooter
from pprint import pprint

class TootCrawler():
    """Class to fetch the recent toots from fedihum.org."""

    def __init__(self, mastodonInstance: any) -> None:
        """Initialize the Mastodon instance and depending classes.

        Parameters
        ------
            mastodonInstance: any
                The initialized Mastodon instance.
        """
        self.mastodonInstance = mastodonInstance
        self.compilePattern = re.compile('<.*?>')
        self.sentiTooter = SentiTooter()
        self.localTimezone = pytz.timezone('Europe/Berlin')

    def getLocalTimeline(self, minId=None) -> any:
        """Receave the local timeline

        Parameters
        ------
            minId: str | None
                The last fetched toot id from the database.

        Returns
        ------
            any
                The local Mastodon timeline from fedihum.org.
        """
        return self.mastodonInstance.timeline_local(min_id=minId, limit=500)

    def cleanhtml(self, raw_html:str) -> str:
        """remove brackets and http string from toots

        Parameters
        ------
            raw_html: str
            The toot content.
        Returns
        ------
            str:
            The cleaned toot content.
        """
        cleantext = re.sub(self.compilePattern, '', raw_html)
        cleantext = re.sub(r'http\S+', '', cleantext)
        return cleantext

    def buildTootsDataframe(self, minId=None) -> DataFrame:
        """Parse fetched toots from Mastodon to dataframe.

        Parameters
        ------
            minId: str | None
            The id of the last fetched toot.

        Returns
        ------
            DataFrame
            A Dataframe containing
            sentiment: str
                The sentiment (positive, neutral, negative)
            model: str
                The used sentiment model.
            toot: str
                The content of the toot.
            datetime: datetime
                The datetime of the toot.
            language: str
                The langage flag of the toot.
            userName: str.
                The user name of the toot.
            userId: str
                The user id.
            tootId: str
                The toot id.
        """
        toots = []
        allTimelineResults = []
        timelinePagination = self.getLocalTimeline(minId)

        while timelinePagination:
            allTimelineResults = allTimelineResults + timelinePagination
            timelinePagination = self.mastodonInstance.fetch_previous(timelinePagination)
        for i in allTimelineResults:
            content = self.cleanhtml(i.content)
            try:
                language = detect(content)
            except:
                language = None
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