from bs4 import BeautifulSoup
import requests
import time
import re
import json

class Rabbithole:
    def __init__(self, start_video, dives):
        self.start_video = start_video
        self.dives = dives
        self.videos = []
        self.go_down_rabbithole()

    def save_json(self, name="result"):
        with open(f'{name}.json', 'w') as fp:
            json.dump(self.videos, fp, indent=4)

    def go_down_rabbithole(self):
        #grab class start video and set to current video
        current_video = self.start_video

        for _ in range(0, self.dives):
            next_video_data = self.find_next_video(current_video)
            self.videos.append(next_video_data)
            current_video = next_video_data["next_link"]
        
        return self.videos

    def find_next_video(self, current_video):
        # stores data for current video
        video_data = {
            "id": len(self.videos) + 1,
            "title": None,
            "channel": None,
            "views": None,
            "category": None,
            "link": current_video,
            "next_link": None
        }

        # Find the next video html
        soup = self.get_soup(current_video)
        next_video_html = self.get_next_video_html(soup)

        # set timeout and counter 
        timeout = 6
        counter = 0
        # make sure next_video_html exists
        while not next_video_html:
            print("Retrying....")
            
            counter += 1
            
            # try until counter exceeds timeout
            if counter <= timeout:
                soup = self.get_soup(current_video)
                next_video_html = self.get_next_video_html(soup)
            
            # go back to the previous video in history and retry
            else:
                previous_video = self.videos[-1]
                print(f"Timeout. Going back 1 video to {previous_video}")
                current_video = previous_video

        # get href and make link for next video
        next_video_href = next_video_html.get('href')
        video_data['next_link'] = 'https://www.youtube.com' + next_video_href

        # Checks if next link is present in our list of dictionaries (history)
        # adapted code from https://stackoverflow.com/questions/3897499/check-if-value-already-exists-within-list-of-dictionaries
        if any(d['link'] == video_data['next_link'] for d in self.videos):
            print(f"{video_data['next_link']} is a duplicate - Retrying ...")
            # get html snippets for all the videos
            videos_html = self.get_next_video_html(soup, return_list=True)
            
            # make a new possible link from the list of videos
            for i in range(0, len(videos_html)):
                possible_new_link = 'https://www.youtube.com' + videos_html[i].get('href')
                
                #if the new possible link has not been visited, make it the next video
                if not any(d['link'] == possible_new_link for d in self.videos):
                    video_data['next_link'] = possible_new_link
        
        #get the rest of the data
        video_data['title'] = soup.find('span', class_='watch-title').text.strip()
        video_data['channel'] = soup.find('div', class_='yt-user-info').text.strip()
        video_data['views'] = soup.find(class_='view-count').text.strip()
        video_data['category'] = self.get_category(soup)

        print(video_data)
        return video_data

    def get_soup(self, current_video):
        # Get web page
        page = requests.get(current_video)
        
        # Print status code for debugging purposes
        print(f"[{str(len(self.videos))}] Request status code for {current_video}: {str(page.status_code)}")
        
        # Parse HTML
        return BeautifulSoup(page.content, 'html.parser')

    def get_next_video_html(self, soup, return_list=None):
        """ This could probably be reworked to use try/except blocks
        Get rid of return_list argument and move logic from find_next-video
        to detect success of html retrieval here.
        """
        if return_list == None:
            return soup.find('a', class_='content-link')
        else:
            return soup.find_all('a', class_='content-link') # should work without 'a' argument   

    def get_category(self, soup):
        #find the h4 element with the text 'Category'
        category_title = soup.find('h4', class_="title", text = re.compile('Category'))
        parent = category_title.parent
        #find category name
        category_value = parent.find('a').text.strip()
        
        return category_value

if __name__ == "__main__":
    
    basketball = Rabbithole("https://www.youtube.com/watch?v=R1KcSa39gkI", 5)
    basketball.save_json()