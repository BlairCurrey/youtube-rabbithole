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
        """
        Could potentially be refactored to check that soup retrieval was succesful and the 
        next video html is accesible and not a duplicate. Could move video data structure 
        and video data retrieval to a new class.
        """
        # stores data for current video
        video = {
            "id": len(self.videos) + 1,
            "link": current_video,
            "next_link": None,
            "title": None,
            "channel": None,
            "views": None,
            "category": None
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
                #don't think this works (rarely gets triggered). see 'timeout_failure_log.txt'
                previous_video = self.videos[-1]
                print(f"Timeout. Going back 1 video to {previous_video}")
                current_video = previous_video

        # get href and make link for next video
        next_video_href = next_video_html.get('href')
        video['next_link'] = 'https://www.youtube.com' + next_video_href

        # Checks if next link is present in our list of dictionaries (history)
        # adapted code from https://stackoverflow.com/questions/3897499/check-if-value-already-exists-within-list-of-dictionaries
        if any(d['link'] == video['next_link'] for d in self.videos):
            print(f"{video['next_link']} is a duplicate - Retrying ...")
            # get html snippets for all the videos
            videos_html = self.get_next_video_html(soup, return_list=True)
            
            # make a new possible link from the list of videos
            for i in range(0, len(videos_html)):
                possible_new_link = 'https://www.youtube.com' + videos_html[i].get('href')
                
                #if the new possible link has not been visited, make it the next video
                if not any(d['link'] == possible_new_link for d in self.videos):
                    video['next_link'] = possible_new_link
        
        #get the rest of the data
        scraped_video = Video_data(video['link'], video['next_link'], soup, len(self.videos) + 1)

        print(scraped_video.data)
        return scraped_video.data

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

class Video_data:
        def __init__(self, start_video, next_video, soup, id_num):
            self.soup = soup
            self.data = {
                "id": id_num,
                "title": None,
                "channel": None,
                "views": None,
                "category": None,
                "link": start_video,
                "next_link": next_video
            }
            self.collect_data()

        def collect_data(self):
            title = self.find_title()
            title_checked = self.handle_failed_scrape(title)
            self.data["title"] = title_checked

            channel = self.find_channel()
            channel_checked = self.handle_failed_scrape(channel)
            self.data["channel"] = channel_checked

            views = self.find_views()
            views_checked = self.handle_failed_scrape(views)
            self.data["views"] = views_checked

            category = self.find_category()
            category_checked = self.handle_failed_scrape(category)
            self.data["category"] = category_checked

        def find_title(self):
            title = self.soup.find('span', class_='watch-title').text.strip()
            return title

        def find_channel(self):
            channel = self.soup.find('div', class_='yt-user-info').text.strip()
            return channel

        def find_views(self):
            views_str = self.soup.find(class_='view-count').text.strip()
            views_split_str = views_str.split()[0]
            views_split_str_no_comma = views_split_str.replace(',','')
            views_num = int(views_split_str_no_comma)
            return views_num

        def find_category(self):
            #find the h4 element with the text 'Category', then find it's parent
            category_title = self.soup.find('h4', class_="title", text = re.compile('Category'))
            parent = category_title.parent
            #find category name from parent
            category = parent.find('a').text.strip()
            return category

        def handle_failed_scrape(self, soup_find_return):
            if soup_find_return is not None:
                return soup_find_return
            else:
                return "[ERROR] Not Found"

if __name__ == "__main__":
    examples = {
        "wolf_hunting": "https://www.youtube.com/watch?v=hMIGbEfikGQ",
        "larry_bird": "https://www.youtube.com/watch?v=R1KcSa39gkI"
    }

    wolf_hunting = Rabbithole(examples["wolf_hunting"], 5)
    wolf_hunting.save_json()
    # wolf_hunting.save_json(name="wolf_hunting")