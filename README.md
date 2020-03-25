# Rabbit hole
a metaphor for something that transports someone into a wonderfully (or troublingly) surreal state or situation
#
Have you ever started watching something on Youtube and ended up engrossed in a completely unrelated video?

Or have you ever read a comment on a video that proclaims something to the effect of "It's 2am on a Tuesday and I have no experience with carpentry but I can't stop learning about Japanese hardware-less joinery techniques"

Well, why not kill all the fun and get straight to the bottom of these time-wasting journeys?

This python program takes a youtube video url as input and a number of "dives" and continues on to the next recommended video that many times. It returns a list of dictionaries which contain data for each video (title, channel name, url, etc).

**Libraries used** 

 - BeautifulSoup
 - requests
 - time
 - json
 - re
	