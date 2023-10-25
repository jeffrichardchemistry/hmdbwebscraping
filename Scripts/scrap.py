from HMDBScraping import Scraping

path2InTimeSave = ''
path2SaveFinishedWork = ''

sc = Scraping(pathname=path2InTimeSave)
get = sc.fit(initialID = 1, finalID = 10000, time2wait = 5)

get.to_csv(path2SaveFinishedWork,index=False,sep=';')