# Rabbit hole
a metaphor for something that transports someone into a wonderfully (or troublingly) surreal state or situation
#
Have you ever started watching something on Youtube and ended up engrossed in a completely unrelated video? Or have you ever read a comment on a video that proclaimed something to the effect of "It's 2am on a Tuesday and I have no experience with carpentry but I can't stop learning about Japanese hardware-less joinery techniques"

Well, why not kill all the fun and get straight to the bottom of these time-wasting journeys?

This python program takes a youtube video url as input and a number of "dives" and continues on to the next recommended video that many times. It returns a list of dictionaries which contain data for each video (title, channel name, url, etc).

**Libraries used** 

 - BeautifulSoup
 - requests
 - time
 - json
 - re
 - logging

## Error Handling
This program encounters several errors when scraping youtube. Generally speaking, my aim is to find the information if it exists, skip it if it doesn't, and only change the current video if there is no other way to proceed to the next one. Here are such errors and how my program handles them:

 - **next video scrape fails**
    - Sometimes the scraper cannot find the next video html. This is likely due to ads changing the layout, although this is difficult to reproduce in a browser. In this event, the program will make a new url request and make new soup, then retry scraping the next video up to 5 times. This virtually always solves the problem well before the 5th try. If the request is still not successful an error message is logged.

 - **view count scrape fails**
    - Occasionally the view count is inaccessible from the HTML (despite it being visible when you visit the url in a browser) and I see no apparent way to retrieve it. This is a rare occurence (about 0.5% of the last ~1000 videos I have scraped). When this happens an error message is returned in place of the view count.
