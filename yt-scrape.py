from bs4 import BeautifulSoup
import requests
import time
import re
import json

def save_to_file(video_dictionary):
    with open('result.json', 'w') as fp:
        json.dump(video_dictionary, fp, indent=4)

def youtube_dive(dives, start_video):
    video_list = []

    # Using '_' is the python convention for a placeholder variable (will not be referenced)
    # https://stackoverflow.com/questions/52792987/unused-variable-in-a-for-loop
    for _ in range(0, dives):
        next_video_data = find_next_video(start_video, video_list)
        video_list.append(next_video_data)
        start_video = next_video_data['next_link']
    
    return video_list

def find_next_video(start_video, history):

    video_data = {
        "id": len(history) + 1,
        "title": None,
        "channel": None,
        "views": None,
        "category": None,
        "link": start_video,
        "next_link": None
    }

    # Find the next video html
    soup = get_soup(start_video, history)
    next_video_html = get_next_video_html(soup)

    # set timeout and counter 
    timeout = 6
    counter = 0
    # make sure next_video_html exists
    while not next_video_html:
        print("Retrying....")
        
        counter += 1
        
        # try until counter exceeds timeout
        if counter <= timeout:
            soup = get_soup(start_video, history)
            next_video_html = get_next_video_html(soup)
        
        # go back to the previous video in history and retry
        else:
            previous_video = history[len(history) - 1]
            print("Timeout. Going back 1 video to" + previous_video)
            start_video = previous_video

    # get href and make link for next video
    next_video_href = next_video_html.get('href')
    video_data['next_link'] = 'https://www.youtube.com' + next_video_href

    # Checks if next link is present in our list of dictionaries (history)
    # adapted code from https://stackoverflow.com/questions/3897499/check-if-value-already-exists-within-list-of-dictionaries
    if any(d['link'] == video_data['next_link'] for d in history):
        print(f"{video_data['next_link']} is a duplicate - Retrying ...")
        # get all the videos
        videos_html = get_next_video_html(soup, return_list=True)
        
        # make a new possible link from the list of videos
        for i in range(0, len(videos_html)):
            possible_new_link = 'https://www.youtube.com' + videos_html[i].get('href')
            
            #if the new possible link has not been visited, make it the next video
            if not any(d['link'] == possible_new_link for d in history):
                video_data['next_link'] = possible_new_link
    
    #get the rest of the data
    video_data['title'] = soup.find('span', class_='watch-title').text.strip()
    video_data['channel'] = soup.find('div', class_='yt-user-info').text.strip()
    video_data['views'] = soup.find(class_='view-count').text.strip()
    video_data['category'] = get_category(soup)
    
    #Refactored - creates Video_data instance (overkill) and calls get_category method
    # test = Video_data(start_video, history)
    # video_data['category'] = test.get_category(soup)

    print(video_data)
    return video_data

class Video_data:
        def __init__(self, start_video, history):
            self.start_video = start_video
            self.history = history
            self.data = {
                "id": len(history) + 1,
                "title": None,
                "channel": None,
                "views": None,
                "category": None,
                "link": start_video,
                "next_link": None
            }

        def get_category(self, soup):
            #find the h4 element with the text 'Category', then find it's parent
            category_title = soup.find('h4', class_="title", text = re.compile('Category'))
            parent = category_title.parent
            #find category name from parent
            category_value = parent.find('a').text.strip()

            return category_value

def get_category(soup):
    
    #find the h4 element with the text 'Category'
    category_title = soup.find('h4', class_="title", text = re.compile('Category'))
    parent = category_title.parent
    #find category name
    category_value = parent.find('a').text.strip()
    
    return category_value

def get_next_video_html(soup, return_list=None):
    
    if return_list == None:
        return soup.find('a', class_='content-link')
    else:
        return soup.find_all('a', class_='content-link') # should work without 'a' argument        

def get_soup(start_video, history):
    # Get web page
    page = requests.get(start_video)
    
    # Print status code for debugging purposes
    print(f"[{str(len(history))}] Request status code for {start_video}: {str(page.status_code)}")
    
    # Parse HTML
    return BeautifulSoup(page.content, 'html.parser')

def save_html(soup, url):
    with open('yt-scrape-html.txt','w',encoding='utf-8-sig') as f:
        f.write(url + "\n" + soup.prettify())

if __name__ == "__main__":

    #search by video
    rabbit_hole = youtube_dive(20, start_video="https://www.youtube.com/watch?v=R1KcSa39gkI")
    save_to_file(rabbit_hole)