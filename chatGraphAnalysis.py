from __future__ import print_function

#How to test runs on Digital Ocean (works because of __init__.py - https://stackoverflow.com/questions/4383571/importing-files-from-different-folder)
#from getTwitchChatData.chatGraphAnalysis import getChatGraphAnalysis, subscribersAcrossMultipleVideos
#TESTING
#from getTwitchChatData.chatGraphAnalysis import killAllChromeProcessesEitherOS, getVideosForStreamerBETTER, subscribers, getData, getVideoPath, videoDataExists



#import json
#data = json.load(open('data.json'))

#NEXT STEPS. NEED TO GET BETTER VIDEOS FOR INDIVIDUALS. FOR SOME REASON VIDEOS ARE GARBAGE. SCRAPER (MANUAL) + LONGER = BETTER
#SETUP CHROMEDRIVER SCRAPER TO AUTO WORK (DETECT OS) ON LINUX/OS...
#ADD ABILITY TO TRACK DONATIONS/SUBCRIPTIONS/CHEERS
#CORRELATE GRAPH TO DONATIONS/SUBSCRIPTIONS/CHEERS
# Desired output -> API to get graph analysis of twitch ID
# How it works
# [1] Get videoIDs (only those reaching certain lengths) from TwitchID | (TwitchID -> [VideoID1, VideoID2, ..., VideoIDN])
# [2] Get video chat data from videoID | (videoID -> saved json file of chat data/metadata)
# [3] Analyze video chat data | (saved json file of chat data/metadata -> {transitivity:0.41, density:0.20,...})
# [4] Aggregate results for multiple videoIDs and send API response ([videoAnalysis1, videoAnalysis2, ..., videoAnalysis3] -> {status:200, transitivity:0.43, '...', })

#from chatGraphAnalysis import getVideosForStreamer, readCSV, writeStreamersToCSV, getVideoIDs, uniqueCommenters, subscribers, findCommentsWithText, findFullTextCommentsWithText,getGraph, getHistogram, createGraphNX,getGraphTheoryMetrics,getData,metricsFromVideoID,updateExcel
def getSoupFromUrl(url):
	from sys import platform
	from bs4 import BeautifulSoup
	import requests
	from time import sleep
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	from random import randint
	import os
	import random
	from pyvirtualdisplay import Display
	from selenium import webdriver 
	if platform == 'darwin':
		chromedriver = "/Users/brandonfreiberg/python-projects/chromedriver"
		os.environ["webdriver.chrome.driver"] = chromedriver
		driver = webdriver.Chrome(chromedriver)
	else:
		display = Display(visible=0, size=(800, 600))
		display.start()
		driver = webdriver.Chrome()
	driver.get(url)
	sleep(randint(2,3))#1-5 seconds
	soup=BeautifulSoup(driver.page_source)
	driver.quit()
	return soup

def killAllChromeProcessesEitherOS():
	def killAllChromeDigitalOcean():
		import subprocess
		import os
		import signal
		ps = subprocess.Popen(['ps', 'aux', '--sort', '-rss'], stdout=subprocess.PIPE).communicate()[0]
		processes = ps.split('\n')
		processesSplit = [processesRow.split() for processesRow in processes[1:]]
		for process in processesSplit:
			if (('-nolisten' in process) and ('-screen' in process)):
				os.kill(int(process[1]), signal.SIGTERM)
		return 'Killed all Chrome processes'
	def killAllChromeMac():
		import subprocess
		import os
		import signal
		ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
		processes = ps.split('\n')
		processesSplit = [processesRow.split() for processesRow in processes[1:]]
		for process in processesSplit:
			if ('Chrome' in process):
				os.kill(int(process[1]), signal.SIGTERM)
				print ('Process killed')
		return 'Killed all Chrome processes'
	from sys import platform
	if platform == 'darwin':
		killAllChromeMac()
	elif platform == 'linux' or platform == 'linux2':
		killAllChromeDigitalOcean()
	else:
		print ('Error')
	return

#Uses API, which appears to be semi-garbage
def getVideosForStreamer(channelID):#channelID = twitchusername
	import json
	import requests
	url = 'https://api.twitch.tv/kraken/channels/%s/videos?client_id=fcz7aihokd8b4mm17brs0xoxav791m' % channelID
	r = requests.get(url)
	jsonObject = r.json()
	videoIDs = []
	if 'videos' in jsonObject.keys():
		for video in jsonObject['videos']:
			videoIDs.append(video['_id'][1:])
	return videoIDs

#Uses scraper
def getVideosForStreamerBETTER(twitchName):
	from bs4 import BeautifulSoup
	# Kill all chrome processes
	killAllChromeProcessesEitherOS()
	# Get videoIDs
	url = 'https://www.twitch.tv/%s/videos/all' % twitchName
	try:
		videoIDs = []
		soup = getSoupFromUrl(url)
		durations = [span.text for span in soup.find_all("span", {"data-a-target":"tw-stat-value"})][1::2]
		links = [a['href'][len('/videos/'):] for a in soup.find_all("a", {"data-a-target":"video-preview-card-image-link"})]
		linksCleaned = []
		for link in links:
			if '?' in link:
				linksCleaned.append(link[:link.find('?')])
			else:
				linksCleaned.append(link)
		for i in range(len(linksCleaned)):
			# If len of vide is at least one hour
			if len(durations[i]) >= 6:
				videoIDs.append(linksCleaned[i])
	except:
		videoIDs = []
	return videoIDs

def readCSV(csvFileName):
	import csv
	csvdataRows = []
	with open(csvFileName, 'rb') as csvfile:
		spamreader = csv.reader(csvfile)
		#for line in data:
		for row in spamreader:
			csvdataRows.append(row)
	## Return rows #
	return csvdataRows

def writeStreamersToCSV(csvFileName, csvdataRows):
	import csv
	with open(csvFileName, 'wb') as csvfile:
		spamwriter = csv.writer(csvfile)
		for row in csvdataRows:
			try:
				spamwriter.writerow(row)
			except:
				wooba = 2+2
	return

# Get video IDs
def getVideoIDs():
	import json
	import requests
	csvFileName = 'streamerEngagementData.csv'
	streamerEngagementData = readCSV(csvFileName)
	for row in streamerEngagementData[1:]:
		twitchName = row[0]
		videoIDs = getVideosForStreamer(twitchName.replace('\t',''))
		for videoID in videoIDs:
			row.append(videoID)
		writeStreamersToCSV(csvFileName, streamerEngagementData)
	return streamerEngagementData

#keys = [u'commenter', u'more_replies', u'channel_id', u'created_at', u'content_offset_seconds', u'updated_at', u'_id', u'source', u'state', u'content_type', u'message', u'content_id']
#Important in first analysis = commenter, message = {'body', 'user_badges':['subscriber']}
##How many times is a user mentioned in another user's comments

def uniqueCommenters(data):
	uniqueCommentersList = list(set([comment['commenter']['name'] for comment in data[1:]]))
	return uniqueCommentersList

def subscribers(data):
	subscribersComments = []
	for commenter in data[1:]:
		if 'user_badges' in commenter['message']:
			#userBadges = [subBadge in [badge.values() for badge in commenter['message']['user_badges']]]
			def getUserBadgesList(commenter):
				userBadgesList = []
				for dictionary in commenter['message']['user_badges']:
					for value in dictionary.values():
						userBadgesList.append(value)
				return userBadgesList
			userBadgesList = getUserBadgesList(commenter)
			if 'subscriber' in userBadgesList:
				subscribersComments.append(commenter)
	uniqueSubscribersList = list(set(comment['commenter']['name'] for comment in subscribersComments))
	return subscribersComments, uniqueSubscribersList

#Things to look at
#is_action,
def emoteDictionary(data):
	actions = []
	for commenter in data[1:]:
		if (commenter['message']['is_action'] == True):
			actions.append(commenter)
	return actions
	for commenter in data[1:]:
		if 'user_badges' in commenter['message']:
			#userBadges = [subBadge in [badge.values() for badge in commenter['message']['user_badges']]]
			def getUserBadgesList(commenter):
				userBadgesList = []
				for dictionary in commenter['message']['user_badges']:
					for value in dictionary.values():
						userBadgesList.append(value)
				return userBadgesList
			userBadgesList = getUserBadgesList(commenter)
			if 'subscriber' in userBadgesList:
				subscribersComments.append(commenter)
	uniqueSubscribersList = list(set(comment['commenter']['name'] for comment in subscribersComments))
	return emoteDictionary

def findCommentsWithText(data,text):
	#Unique commenters = edges
	#uniqueCommenters = uniqueCommenters(data)
	messages = []
	for message in [comment['message']['body'] for comment in data[1:]]:
		if text.lower() in message.lower():
			messages.append(message)
	return messages

def findFullTextCommentsWithText(data,text):
	#Unique commenters = edges
	#uniqueCommenters = uniqueCommenters(data)
	messages = []
	for comment in data[1:]:
		if text.lower() in comment['message']['body']:
			messages.append(comment)
	return messages

# Graph Theory #
# Define graph = {'a':['c'], 'b':['c','e'], ..., 'f':[]}
def getGraph(data):
	graph = {}
	nodes = [node.lower() for node in uniqueCommenters(data)]
	# Directionless graph
	# [1] Initialize graph
	for node in nodes:
		graph[node] = []
	# [2] Add nodes to graph
	for comment in data[1:]:
		name = comment['commenter']['name'].lower()
		message = comment['message']['body'].lower()
		for node in graph.keys():
			if node in message:
				# [A] Add commenter to node connection
				graph[name].append(node)
				# [B] Add commentee to node connection
				graph[node].append(name)
	return graph

def numberOfMentions(graph):
	mentions
	for commenter in graph.keys():
		mentions+=len(graph[commenter])
	return mentions
# Graph metrics (to compare graph 1 to graph n)

# Histogram
def getHistogram(graph):
	histogram = sorted([len(value) for value in graph.values()])
	return histogram

# Graph density
# Distance/diameter
# Clustering

#G.add_edges_from([(1,2),(1,3)])
def createGraphNX(graph):
	import networkx as nx
	G=nx.Graph()
	for key in graph.keys():
		for element in graph[key]:
			G.add_edge(key,element)
	return G

def getGraphTheoryMetrics(G):
	from networkx import density, degree_histogram, degree, info, triangles, transitivity, average_clustering
	graphTheoryMetrics = {'density':density(G), 'transitivity':transitivity(G), 'average_clustering':average_clustering(G)}
	return graphTheoryMetrics

# ALL AT ONCE #
def getData(videoID):
	import requests
	import sys
	import calendar
	import time
	import math
	import json

	#data = json.load(open('data.json'))
	#https://api.twitch.tv/v5/videos/201052159/comments?client_id=fcz7aihokd8b4mm17brs0xoxav791m

	CHUNK_ATTEMPTS = 6
	CHUNK_ATTEMPT_SLEEP = 10
	    
	messages = []

	cid = "fcz7aihokd8b4mm17brs0xoxav791m"
	vod_info = requests.get("https://api.twitch.tv/kraken/videos/v" + str(videoID), headers={"Client-ID": cid}).json()

	#file_name = "rechat-" + str(videoID) + ".json"
	from sys import platform
	if platform == 'darwin':
		file_name = 'rechat-%s.json' % str(videoID)
	else:
		file_name = 'getTwitchChatData/chatLogs/rechat-%s.json' % str(videoID)	

	messages.append(vod_info)   # we store the vod metadata in the first element of the message array

	response = None

	print("downloading chat messages for vod " + str(videoID) + "...")
	while response == None or '_next' in response:
	    query = ('cursor=' + response['_next']) if response != None and '_next' in response else 'content_offset_seconds=0'
	    for i in range(0, CHUNK_ATTEMPTS):
	        error = None
	        try:
	            response = requests.get("https://api.twitch.tv/v5/videos/" + str(videoID) + "/comments?" + query, headers={"Client-ID": cid}).json()
	        except requests.exceptions.ConnectionError as e:
	            error = str(e)
	        else:
	            if "errors" in response or not "comments" in response:
	                error = "error received in chat message response: " + str(response)
	        
	        if error == None:
	            messages += response["comments"]
	            break
	        else:
	            print("\nerror while downloading chunk: " + error)
	            
	            if i < CHUNK_ATTEMPTS - 1:
	                    print("retrying in " + str(CHUNK_ATTEMPT_SLEEP) + " seconds ", end="")
	            print("(attempt " + str(i + 1) + "/" + str(CHUNK_ATTEMPTS) + ")")
	            
	            if i < CHUNK_ATTEMPTS - 1:
	                time.sleep(CHUNK_ATTEMPT_SLEEP)

	print()
	print("saving to " + file_name)

	f = open(file_name, "w")
	f.write(json.dumps(messages))
	f.close()

	print("done!")
	return

def metricsFromVideoID(videoID):
	csvFileName = 'rechat-%s.json' % str(videoID)
	# If videoID json doesn't exist, download
	import os.path
	if os.path.isfile(csvFileName) == False:
		getData(videoID)
	import json
	data = json.load(open(csvFileName))
	graph = getGraph(data)
	G = createGraphNX(graph)
	graphTheoryMetrics = getGraphTheoryMetrics(G)
	return graphTheoryMetrics

def updateExcel():
	import json
	import requests
	from numpy import median
	csvFileName = 'streamerEngagementData.csv'
	streamerEngagementData = readCSV(csvFileName)
	for row in streamerEngagementData[1:]:
		twitchName = row[0]
		videoIDs = row[5:]
		densityList = []
		transitivityList = []
		average_clusteringList = []
		for videoID in videoIDs:
			if videoID != "":
				try:
					graphTheoryMetrics = metricsFromVideoID(videoID)
					densityList.append(graphTheoryMetrics['density'])
					transitivityList.append(graphTheoryMetrics['transitivity'])
					average_clusteringList.append(graphTheoryMetrics['average_clustering'])
				except:
					wooba = 2+2
		row[1] = median(densityList)
		row[2] = median(transitivityList)
		row[3] = median(average_clusteringList)
		#print twitchName, median(densityList), median(transitivityList), median(average_clusteringList)
		writeStreamersToCSV(csvFileName, streamerEngagementData)
	return streamerEngagementData

def getVideoPath(videoID):
	from sys import platform
	if platform == 'darwin':
		videoPath = 'rechat-%s.json' % str(videoID)
	else:
		videoPath = 'getTwitchChatData/chatLogs/rechat-%s.json' % str(videoID)
	return videoPath
def videoDataExists(videoID):
	videoPath = getVideoPath(videoID)
	import os.path
	if os.path.isfile(videoPath):
		return True
	else:
		return False
#UPDATE GET DATA TO INCORPORATE LINUX/OS DISSONANCE
def getChatGraphAnalysis(twitchName):
	# [1] Get video IDs that are at least 1 hour long
	videoIDs = getVideosForStreamerBETTER(twitchName)
	# [2] Download chat data for videos - HOW MANY VIDEOS NECESSARY? 5?
	videoIDsToAnalyze = videoIDs[:max(5,min(len(videoIDs),0))]
	[getData(videoID) for videoID in videoIDsToAnalyze if (videoDataExists(videoID) == False)]
	# [3] Create graphs for each video
	import json
	chatTheoryMetricsList = []
	for videoID in videoIDsToAnalyze:
		print ('Analyzing graph for' + str(videoID))
		data = json.load(open(getVideoPath(videoID)))
		graph = getGraph(data)
		G = createGraphNX(graph)
		graphTheoryMetrics = getGraphTheoryMetrics(G)
		chatTheoryMetricsList.append(graphTheoryMetrics)
	# [4] Aggregate results
	# [4A] Create {'transitivity':[0.3,0.4,0.5], 'density':[0.1,0.0,4.3],...,}
	chatGraphAnalysis = {}
	for graphTheoryMetrics in chatTheoryMetricsList:
		for key in graphTheoryMetrics.keys():
			if key not in chatGraphAnalysis.keys():
				chatGraphAnalysis[key] = [graphTheoryMetrics[key]]
			else:
				chatGraphAnalysis[key].append(graphTheoryMetrics[key])
	# [4B] Average lists
	def mean(list):
		return float(sum(list))/max(len(list),1)
	for key in chatGraphAnalysis.keys():
		chatGraphAnalysis[key] = mean(chatGraphAnalysis[key])
	return chatGraphAnalysis

#("twitchName" -> [subscriberComments], [subscriber1, subscriber2, ..., subscriberN])
def subscribersAcrossMultipleVideos(twitchName):
	# [1] Get list of past 5 videos (within certain parameters)
	videoIDs = getVideosForStreamerBETTER(twitchName)
	# [2] For each video get data if doesn't already exist
	videoIDsToAnalyze = videoIDs[:max(5,min(len(videoIDs),0))]
	[getData(videoID) for videoID in videoIDsToAnalyze if (videoDataExists(videoID) == False)]
	# [3] Create subscriber lists for each video
	import json
	subscribersList = []
	for videoID in videoIDsToAnalyze:
		data = json.load(open(getVideoPath(videoID)))
		subscribersComments, uniqueSubscribersList = subscribers(data)
		subscribersList.append([subscribersComments, uniqueSubscribersList])
	# [4] Aggregate lists
	subscribersCommentsAggregated = []
	uniqueSubscribersListAggregated = []
	for element in subscribersList:
		subscribersCommentsAggregated += element[0]
		uniqueSubscribersListAggregated += element[1]
	uniqueSubscribersListAggregated = list(set(uniqueSubscribersListAggregated))
	return subscribersCommentsAggregated, uniqueSubscribersListAggregated

def getFilePath(csvFileName):
	from sys import platform
	if platform == 'darwin':
		filePath = csvFileName
	else:
		filePath = 'getTwitchChatData/' + csvFileName
	return filePath

#csvFileName = 'twingeDataAnalyzedv2.csv'
def recordVideosToAnalyze(csvFileName):
	# [1] Determine CSV File path
	csvFileName = getFilePath(csvFileName)
	csvdataRows = readCSV(csvFileName)
	# [2] Update rows
	for row in csvdataRows[1:]:
		# If blank
		if row[7] == '':
			# If meets certan criteria (average concurrents between x and y)
			averageConcurrents = row[4]
			if (averageConcurrents != '') and (int(averageConcurrents) > 100) and (int(averageConcurrents) <= 300):
				twitchName = row[0]
				videoIDs = getVideosForStreamerBETTER(twitchName)
				videoIDsToAnalyze = videoIDs[:max(5,min(len(videoIDs),0))]
				row[7] = len(videoIDsToAnalyze)
				print (twitchName + ' done')
		# [3] Save (each row)
		writeStreamersToCSV(csvFileName, csvdataRows)
	return csvdataRows

def correlation(csvFileName):
	# DETERMINE CSVFILENAME PATH
	csvFileName = getFilePath(csvFileName)
	csvdataRows = readCSV(csvFileName)
	for row in csvdataRows[1:]:
		twitchName = row[0]
		# If subscribers == empty AND (currentViewers is integer) and (cuncurrentViewers > , get data
		try:
			row[15] = int(row[15])
		except:
			row[15] = '0'
		if (row[7] == '') and (int(row[15]) >= 25) and (int(row[15]) < 500):
			print (twitchName, row[15])
			# [1] Get # of videos analyzed
			videoIDs = getVideosForStreamerBETTER(twitchName)
			videoIDsToAnalyze = videoIDs[:max(5,min(len(videoIDs),0))]
			row[7] = len(videoIDsToAnalyze)
			# [2] Estimate subscribers
			subscribersCommentsAggregated, uniqueSubscribersListAggregated = subscribersAcrossMultipleVideos(twitchName)
			row[8] = len(uniqueSubscribersListAggregated)
			# [3] Graph connectedness
			chatGraphAnalysis = getChatGraphAnalysis(twitchName)
			if 'average_clustering' in chatGraphAnalysis.keys():
				row[9] = chatGraphAnalysis['average_clustering']
			if 'transitivity' in chatGraphAnalysis.keys():
				row[10]  = chatGraphAnalysis['transitivity']
			if 'density' in chatGraphAnalysis.keys():
				row[11] = chatGraphAnalysis['density']
	# Save
	writeStreamersToCSV(csvFileName, csvdataRows)
	return csvdataRows
