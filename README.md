# Rabbit hole
a metaphor for something that transports someone into a wonderfully (or troublingly) surreal state or situation
#
Have you ever started watching something on Youtube and ended up engrossed in a completely unrelated video? Or have you ever read a comment on a video that proclaims something to the effect of "It's 2am on a Tuesday and I have no experience with carpentry but I can't stop learning about Japanese hardware-less joinery techniques"

Well, why not kill all the fun and get straight to the bottom of these time-wasting journeys?

This python program takes a youtube video url as input and a number of "dives" and continues on to the next recommended video that many times. It returns a list of dictionaries which contain data for each video (title, channel name, url, etc).

**Libraries used** 

 - BeautifulSoup
 - requests
 - time
 - json
 - re

## Errors and How They Are Handled
This program encounters several errors when scraping youtube. Here are such errors and how my program handles them:
 - **requests.get(url) fails**
    - Retries the same request 5 times. This virtually always solves the problem within a couple tries. If the request is still not successful the program goes backwards to the previous video, collects the list of recommended videos, and picks a different url to pass to requests.get(). This has not been fully tested and if the request fails 5 times there is probably something else wrong anyways.

 - **view count scrape fails**
    - Occasionally the view count is inaccessible from the HTML and I see no apparent way to retrieve it. This is a rare occurence (about 0.5% of the last ~1000 videos I have scraped). When this happens an error message is returned in place of the view count.