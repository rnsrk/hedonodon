from CRUDManager import CRUDManager
from datetime import datetime
from DbSetup import init_db
import locale
from MastodonAccountManager import MastodonAccountManager
import matplotlib.pyplot as plt
from TootCrawler import TootCrawler
from sqlalchemy.sql import desc, select

locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
init_db()

mastodonAccountManager = MastodonAccountManager()
mastodonInstance = mastodonAccountManager.instance
"""
mastodonInstance.log_in(
    'USER-EMAIL',
    'PW',
    to_file = 'hedonodon_usercred.secret'
)
"""

tootCrawler = TootCrawler(mastodonInstance)
crudManager = CRUDManager()

lastTootId = crudManager.getLastToot()
tootsDataframe = tootCrawler.buildTootsDataframe(lastTootId)
sentimentsYesterday = crudManager.calculateAggregates('sentiment', 'Count')
compoundsYesterday = crudManager.calculateAggregates('compound', 'Avg')
if not tootsDataframe.empty:
     crudManager.saveToDatabase(tootsDataframe, 'Toots', useIndex=False)
     crudManager.saveToDatabase(dataframe=sentimentsYesterday, table='Sentiments', useIndex=True)
     crudManager.saveToDatabase(dataframe=compoundsYesterday, table='Compounds', useIndex=True)
     #print(sentimentsYesterday, 'sentimentsYesterday')
     #print(compoundsYesterday, 'sentimentsYesterday')
else:
     print('Nothing changed since last database insert!')

TodayDate= datetime.strptime(sentimentsYesterday['date'][0], '%Y-%m-%d').strftime('%d.%m.%Y')
dataframe4PieChart = sentimentsYesterday.drop('date', axis=1).set_index('sentiment')
dataframe4LineChart = crudManager.loadFromDatabase('Compounds', 'date').drop('index', axis=1)

fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10,10))

pieChartlabels = dataframe4PieChart.index.to_numpy()
pieChart = dataframe4PieChart.plot.pie(ax=axes[0], y='sentimentCount', ylabel="", labels=dataframe4PieChart['sentimentCount'], title=f'Moods of the toots on {TodayDate} of the local timeline on fedihum.org', colors = ['red', 'grey', 'green'])
chartBox = axes[0].get_position()
axes[0].set_position([chartBox.x0,chartBox.y0-0.2,chartBox.width,chartBox.height])
axes[0].legend(pieChartlabels,loc='upper right', bbox_to_anchor=(1.3, 0.9))
lineChart = dataframe4LineChart.plot.line(ax=axes[1], title='Compounds from max positive (1) to min neg (-1)')
axes[1].set_ylim([-1, 1])

plotFileUrl = f'./plots/{TodayDate}.png'
plt.savefig(plotFileUrl)

media = mastodonInstance.media_post(plotFileUrl, mime_type="image/png", description=f"Sentiment analysis of local timeline on fedihum.org, showing the moods of the toots on, and the compounds up to {TodayDate}.")
mastodonInstance.status_post(f'The moods of the toots on and up to {TodayDate}.', media_ids=media, language='en')