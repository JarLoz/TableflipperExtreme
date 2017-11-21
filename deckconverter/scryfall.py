import os
import requests
import json

scryfallCache = None

def doRequest(url, params=None):
    """
    Does a request to scryfall card API. The module maintains a cache in the scryfallCache dictionary,
    initialized by reading the scryfallCache.json file. Any request is first checked from the cache
    before doing the actual request.
    """
    global scryfallCache
    if scryfallCache == None:
        if os.path.isfile('scryfallCache.json'):
            with open('scryfallCache.json',encoding='utf8') as cacheFile:
                scryfallCache = json.load(cacheFile)
        else:
            scryfallCache = {}
    urlBuggered = url.replace('/','.').replace(':','.')
    if (params != None):
        paramsBuggered = params['q'].replace(' ','').replace(':','.').replace('"','').replace("'",'')
        cacheKey = urlBuggered+paramsBuggered
    else:
        cacheKey = urlBuggered

    if cacheKey in scryfallCache.keys():
        print ('Cache hit!')
        return scryfallCache[cacheKey]

    response = requests.get(url,params).json()
    if response['object'] != 'error':
        scryfallCache[cacheKey] = response

    return response

def dumpCacheToFile():
    """
    Dumps the cache dictionary to an external file. This function needs to be called before
    exiting the application in order to have any use of the cache.
    """
    global scryfallCache
    if len(scryfallCache) > 0:
        with open('scryfallCache.json', 'w',encoding='utf8') as outfile:
            json.dump(scryfallCache, outfile)
        print('Cache dumped')

def bustCache():
    """
    Initializes the cache dictionary as an empty dictionary, effectively bypassing the
    cache file written to the disk. For debugging purposes.
    """
    global scryfallCache
    scryfallCache = {}
