from HMDBScraping import Scraping
import prctl
prctl.set_name("JeffWebScraping")

path2InTimeSave = '/home/jeff/works/webscraping_hmdb/hmdbwebscraping/Scripts/data/InTimedata_1to10000.txt'
path2SaveFinishedWork = '/home/jeff/works/webscraping_hmdb/hmdbwebscraping/Scripts/data/finished_data_1to10000.csv'

sc = Scraping(pathname=path2InTimeSave)
get = sc.fit(initialID = 1, finalID = 10000, time2wait = 7)

get.to_csv(path2SaveFinishedWork,index=False,sep=';')
