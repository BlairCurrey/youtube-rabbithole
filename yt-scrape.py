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
        with open(f'results/{name}.json', 'w') as fp:
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
                #May not work ...
                previous_video = self.videos[-1]
                print(f"Timeout. Going back 1 video to {previous_video}")
                current_video = previous_video
                #remake soup and assign html
                soup = self.get_soup(current_video)
                next_video_html = self.get_next_video_html(soup)

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
        scraped_video = Video_data(video['link'], video['next_link'], soup, video['id'])

        print(scraped_video.data)
        return scraped_video.data

    def get_soup(self, current_video):
        # Get web page
        page = requests.get(current_video)
        
        # Print status code for debugging purposes
        print(f"[{len(self.videos) + 1}] Request status code for {current_video}: {str(page.status_code)}")
        
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
            self.failed_scrape_message = "[ERROR] Not Found"
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
            self.data["title"] = self.find_title()
            self.data["channel"] = self.find_channel()
            self.data["views"] = self.find_views()
            self.data["category"] = self.find_category()

        def find_title(self):
            title = self.soup.find('span', class_='watch-title').text.strip()
            return title

        def find_channel(self):
            channel = self.soup.find('div', class_='yt-user-info').text.strip()
            return channel

        def find_views(self):
            views_str = self.soup.find(class_='watch-view-count')
            # occasionally watch-view-count does not exist or doesn't 
            # contain views (and the one displayed cannot be found in soup)
            if views_str and self.has_numbers(views_str.text):
                views_str_strip = views_str.text.strip()
                views_split_str = views_str_strip.split()
                views_split_str_no_comma = views_split_str[0].replace(',','')
                views_num = int(views_split_str_no_comma)
                return views_num
            else:
                return self.failed_scrape_message

        def find_category(self):
            #find the h4 element with the text 'Category', then find it's parent
            category_title = self.soup.find('h4', class_="title", text = re.compile('Category'))
            parent = category_title.parent
            #find category name from parent
            category = parent.find('a').text.strip()
            return category

        def has_numbers(self, inputString):
            return any(char.isdigit() for char in inputString)

if __name__ == "__main__":
    examples = {
        "wolf_hunting": "https://www.youtube.com/watch?v=hMIGbEfikGQ",
        "larry_bird": "https://www.youtube.com/watch?v=R1KcSa39gkI",
        "ancient_aliens": "https://www.youtube.com/watch?v=AdsBmlejPGA",
        "ray_mears": "https://www.youtube.com/watch?v=UsbSMplJ6g4",
        "forklift_safety": "https://www.youtube.com/watch?v=fPhynD2yuBE"
    }

    for key in examples:
        dives = 10
        test = Rabbithole(examples[key], dives)
        test.save_json(name=f"{key}-{dives}")
    
    # test = Rabbithole("https://www.youtube.com/watch?v=yFYb5Pk3LUM", 5)
    # test.save_json(name="forklift_safety-500")