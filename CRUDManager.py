from DbSetup import connection, engine, session, databaseUrl
import pandas as pd
from sqlalchemy import desc, select, sql
from Tables import Toots


def calculateSentimentCount():
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

def calculateSentimentMean(dataframe):
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

class CRUDManager():

    def saveToDatabase(self, dataframe, table:str, useIndex=False):
        try:
            dataframe.to_sql(table, engine, index=useIndex, if_exists="append")
        except:
            print(f'Could not save data to {table}!')

    def loadFromDatabase(self, table:str, indexColumn=None):
        return pd.read_sql_table(table, connection, index_col=indexColumn)

    def getLastToot(self):
        stmt = select(Toots.tootId).order_by(desc('datetime'))
        return session.scalars(stmt).first()
