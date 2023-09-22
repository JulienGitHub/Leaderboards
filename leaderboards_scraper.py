import ftplib
import requests
import json
from datetime import datetime
import time
import os
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from random import randrange

regions = ['AP', 'NA', 'EU', 'LA','SO']
products = ['tcg', 'vg']
leagues = ['junior', 'senior', 'master']

class Point:
	def __init__(self, points, date):
		self.points = points
		self.date = date
		
	def toJSON(self):
		return '{"date":"'+str(self.date)+'", "points":'+str(self.points)+'}'

class Player:
	def __init__(self, name, country, region, product, league):
		self.name = name    
		self.country = country
		self.region = region
		self.product = product
		self.league = league
		self.Points = []
	
	def addPoints(self, points, date):
		self.Points.append(Point(points, date))
	
	def toJSON(self):
		output = '{"name":"'+self.name.replace('\\', '')+'", "country":"'+self.country+'", "region":"'+self.region+'","product":"'+self.product+'","league":"'+self.league+'","points":['
		strPoints = ''
		for p in self.Points:
			if(len(strPoints) > 0):
				strPoints += ','
			strPoints += p.toJSON()
		output += strPoints+']}'
		return output

players = []

#missing : retrieving leaderboards.json from pokedata

if (os.path.exists('leaderboards.json') == False):
	f = open('leaderboards.json', 'w')
	f.write('[]')
	f.close()

with open('leaderboards.json', encoding='utf-8') as f:
	leaderboardsData = json.load(f)
	for player in leaderboardsData:
		p = Player(player['name'], player['country'], player['region'], player['product'], player['league'])
		for points in player['points']:
			p.addPoints(points['points'], points['date'])
		players.append(p)


while(True):
	try:
		timecode = datetime.today().strftime('%Y%m%d-%H%M%S')
		jsonTime = datetime.now()

		driver = Driver(uc=True)

		for product in products:
			for region in regions:
				for league in leagues:
					url = 'https://www.pokemon.com/fr/play-pokemon/classements/op/api/'+product+'-'+league+'/?leaderboard_type=championship&leaderboard_when=107&leaderboard_who=&per_page=5000&page=1&include=metadata&format=json&zone=REGION-'+region
					print(url)
					driver.get(url)
					time.sleep(30+randrange(60))
					data_json = json.loads(driver.find_element(By.TAG_NAME, 'pre').text)
					for player in data_json['leaderboard']['records']:
						player['screen_name'] = player['screen_name'].replace("\\'", "'")
						l = list(filter(lambda x:x.name==player['screen_name'] and x.country == player['country'] and x.region == region and x.product == product and x.league == league, players))
						if(l is not None and len(l) > 0):
							if(l[0].Points[len(l[0].Points)-1].points < player['score']):
								l[0].addPoints(player['score'], jsonTime)
						else:
							p = Player(player['screen_name'], player['country'], region, product, league)
							p.addPoints(player['score'], jsonTime)
							players.append(p)								
		with open('leaderboards.json', 'w', encoding='utf-8') as data_file:
			data_file.write('[')
			b = 0
			for p in players:
				if(b == 1):
					data_file.write(',')
				data_file.write(p.toJSON())
				b = 1
				
			data_file.write(']')
		driver.close()

	except Exception as e: print(e)

	print(timecode)
	time.sleep(24*60*60)

