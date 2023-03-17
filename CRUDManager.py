from DbSetup import connection, engine, session, databaseUrl
import pandas as pd
from sqlalchemy import desc, select, sql
from Tables import Toots

from pandas.core.api import (
    DataFrame)

def calculateSentimentCount():
    """Calculates the frequencies of the sentiments.

    Returns
    -------
    DataFrame
        Containing date (YY-MM-DD), sentiment (positive, neutral, negative),
        and sentimentCount.
    """

    query = f'''SELECT DATE(datetime) as date, sentiment, COUNT(sentiment) as sentimentCount
                FROM Toots
                GROUP BY DATE(datetime),
                sentiment
                HAVING datetime >= DATE("now","-1 day")
                AND datetime < DATE("now")'''
    return pd.read_sql(
        sql.text(query),
        connection,
        parse_dates=["datetime"]
    )

def calculateSentimentMean(dataframe:DataFrame) -> DataFrame:
    """Calculates the mean of the sentiments.

    Parameters
    -------
        dataframe: DataFrame

    Returns
    -------
        Dataframe
        Containing date (YY-MM-DD), sentimentsMean.
    """
    negativeSentimentSum = dataframe[dataframe['sentiment'] == 'negative']['sentimentCount'].sum() * -1
    positiveSentimentSum = dataframe[dataframe['sentiment'] == 'positive']['sentimentCount'].sum()
    sentimentSum = dataframe['sentimentCount'].sum()
    sentimentMean = (negativeSentimentSum + positiveSentimentSum) / sentimentSum
    sentimentDate = dataframe.loc[0]['date']
    return pd.DataFrame.from_records(
        [
            {
                'date': sentimentDate,
                'sentimentsMean': sentimentMean
            }
        ]
    )

def getYesterdaysToots() -> DataFrame:
    """Fetches yesterdays toots from database.

    Returns
    -------
        pd.Dataframe
        Containing date (YY-MM-DD), language, sentiment, toot.
    """
    query = f'''SELECT datetime as date, language, sentiment, toot
                FROM Toots
                WHERE datetime >= DATE("now","-1 day")
                AND datetime < DATE("now")'''
    return pd.read_sql(
        sql.text(query),
        connection,
        parse_dates=["datetime"]
    )

class CRUDManager():
    """Class for database operations"""

    def saveToDatabase(self, dataframe:DataFrame, table:str, useIndex=False):
        """Saves dataframe to database.

        Parameters
        -------
            dataframe: DataFrame
                Input dataframe.
            table: str
                Table, where to save the data.
            useIndex: boolean
                Should the index of the dataframe be used as index for
                the database table?
        """
        try:
            dataframe.to_sql(table, engine, index=useIndex, if_exists="append")
        except:
            print(f'Could not save data to {table}!')

    def loadFromDatabase(self, table:str, indexColumn=None) -> DataFrame:
        """Load a table into a dataframe.

        Parameters
        -------
            table: str
                Table, where to save the data.
            indexColumn: str | None
                Should the index of the table be used as index for
                the dataframe?
        Returns
        -------
            DataFrame
        """
        return pd.read_sql_table(table, connection, index_col=indexColumn)

    def getLastToot(self) -> str:
        """Query the last toot id from database.

        Results
        -------
            str
            A toot id.
        """
        stmt = select(Toots.tootId).order_by(desc('datetime'))
        return session.scalars(stmt).first()
