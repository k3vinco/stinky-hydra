import urllib2
import json

def getJson(url):
	#Call the API for bike points
	response = urllib2.urlopen(url)
	jsonObject = json.loads(response.read())
	return jsonObject

#Returns a List of Tuples in format e.g. [("BikePoint_1337","London Street"), (...), ...]
def bikePoints(url):
	listBp = []
	bp = getJson(url)
	for bpId in bp:
		listBp.append((bpId['id'], bpId['commonName']))
	return listBp