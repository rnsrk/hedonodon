from DbSetup import engine, session, databaseUrl
import pandas as pd
from sqlalchemy import desc, select
from Tables import Toots

class CRUDManager():

    def saveToDatabase(self, dataframe, table:str, useIndex=False):
        try:
            dataframe.to_sql(table, engine, index=useIndex, if_exists="append")
        except:
            print(f'Could not save data to {table}!')

    def loadFromDatabase(self, table:str, indexColumn=None):
        return pd.read_sql_table(table, databaseUrl, index_col=indexColumn)

    def getLastToot(self):
        stmt = select(Toots.tootId).order_by(desc('datetime'))
        return session.scalars(stmt).first()

    def calculateAggregates(self, column, aggregate='Count'):
        if (aggregate=='Count'):
            addGroup = f', {column} '
        else:
            addGroup = ''
        query = f'''SELECT DATE(datetime) as date {addGroup}, {aggregate}({column}) as {column}{aggregate}
                    FROM Toots
                    GROUP BY DATE(datetime)''' \
                    + addGroup \
                    + '''HAVING datetime >= DATE("now","-1 day")
                    AND datetime < DATE("now")'''
        return pd.read_sql(
            query,
            databaseUrl,
            parse_dates=["datetime"]
            )
