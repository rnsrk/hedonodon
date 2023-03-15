from CRUDManager import CRUDManager, calculateSentimentCount, calculateSentimentMean, calculateWordCount
from datetime import datetime, date
from DbSetup import init_db
import locale
from MastodonAccountManager import MastodonAccountManager
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from TootCrawler import TootCrawler

locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
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

if not tootsDataframe.empty:
    crudManager.saveToDatabase(tootsDataframe, 'Toots', useIndex=False)
else:
    print('Nothing changed since last database insert!')

wordCounts = calculateWordCount()
print(wordCounts);
print("exit programm")
exit()
sentimentsYesterday = calculateSentimentCount()
sentimentMeansYesterday = calculateSentimentMean(sentimentsYesterday)

if not tootsDataframe.empty:
    crudManager.saveToDatabase(dataframe=sentimentsYesterday, table='SentimentCounts', useIndex=True)
    crudManager.saveToDatabase(dataframe=sentimentMeansYesterday, table='SentimentMeans', useIndex=True)
else:
    print('Nothing changed since last database insert!')

colormap = {
    'negative': '#ff9999',
    'neutral': '#ffcc99',
    "positive": '#99ff99'
}

todaysColors = []
for sentiment in sentimentsYesterday['sentiment'].to_numpy():
    todaysColors.append(colormap[sentiment])



TodayDate = datetime.strptime(sentimentsYesterday['date'][0], '%Y-%m-%d').strftime('%d.%m.%Y')
dataframe4PieChart = sentimentsYesterday.drop('date', axis=1).set_index('sentiment')
dataframe4LineChart = crudManager.loadFromDatabase('SentimentMeans', 'date').drop('index', axis=1)

fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))

# Pie chart.
pieChartlabels = dataframe4PieChart.index.to_numpy()
pieChart = dataframe4PieChart.plot.pie(
    ax=axes[0],
    y='sentimentCount',
    ylabel="",
    labels=dataframe4PieChart['sentimentCount'],
    title=f'Moods of the toots on {TodayDate} of the local timeline on fedihum.org',
    colors=todaysColors,
    wedgeprops=dict(linewidth=3, edgecolor='w'),
    startangle=90
)

axes[0].axis('equal')
centre_circle = plt.Circle((0, 0), 0.6, fc='white')
axes[0].add_patch(centre_circle)
chartBox = axes[0].get_position()
axes[0].legend(pieChartlabels, loc='upper right', bbox_to_anchor=(0.9, 0.9))

# Line chart.
lineChart = dataframe4LineChart.plot.line(
    ax=axes[1],
    title='"Mean" of sentiments, calculated from nominal values, pos(1), neu (0), neg (-1)!'
)
axes[1].grid(True)
axes[1].set_xlim([date(2023, 1, 1), date(2023, 12, 31)])
axes[1].set_ylim([-1, 1])
axes[1].xaxis.set_major_locator(mdates.MonthLocator())
axes[1].xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=15))
axes[1].xaxis.set_major_formatter(plt.NullFormatter())
axes[1].xaxis.set_minor_formatter(mdates.DateFormatter('%h'))
axes[1].tick_params(which='minor', length=0)
plotFileUrl = f'./plots/{TodayDate}.png'
plt.savefig(plotFileUrl)

#media = mastodonInstance.media_post(plotFileUrl, mime_type="image/png", description=f"Sentiment analysis of local timeline on fedihum.org, showing the moods of the toots on, and the sentiment mean up to {TodayDate}.")
#mastodonInstance.status_post(f'The moods of the toots on and up to {TodayDate}.', media_ids=media, language='en')

