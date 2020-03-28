from bs4 import BeautifulSoup
import requests
import time
import re
import json

class RabbitHole:
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
        # stores data for current video
        video = {
            "id": len(self.videos) + 1,
            "link": current_video,
            "next_link": None,
            "soup": None
        }

        # Get soup and find the next video html
        video["soup"] = self.get_soup(video["link"])
        next_video_html = self.find_next_video_html(video["soup"])
        
        # Find new video html and soup if first attempt yields None
        if next_video_html is None:
            next_video_html, video["soup"] = self.retry_find_next_video_html(video["soup"], video["link"], next_video_html)

        # Find new video if it is a YouTube Movie or duplicate
        if self.video_is_youtube_movie(next_video_html) or self.video_is_duplicate(next_video_html):
            next_video_html = self.pick_next_video_html_from_list(video["soup"])
        
        video["next_link"] = self.make_link_from_html(next_video_html)
        
        #get the rest of the data
        scraped_video = VideoData(video['link'], video['next_link'], video["soup"], video['id'])

        print(scraped_video.data)
        return scraped_video.data
    
    def get_soup(self, current_video):
        # Get web page
        page = requests.get(current_video)
        
        # Print status code for debugging purposes
        print(f"[{len(self.videos) + 1}] Request status code for {current_video}: {str(page.status_code)}")
        
        # Parse HTML
        return BeautifulSoup(page.content, 'html.parser')

    def find_next_video_html(self, soup):
        return soup.find('a', class_='content-link')
        
    def find_next_video_html_list(self, soup):
        return soup.find_all('a', class_='content-link')

    def retry_find_next_video_html(self, soup, current_video, html):
        attempts = 0
        threshold = 5

        while attempts < threshold:
            attempts += 1
            
            if html is None:
                print("Failed to get next video. Making new soup and Retrying ...")
                new_soup = self.get_soup(current_video)
                html = self.find_next_video_html(new_soup)
                if html:
                    return html, new_soup
            else:
                print(f"Could not find video html in {threshold} attempts")
    
    def make_link_from_html(self, next_video_html):
        href = next_video_html.get('href')
        return 'https://www.youtube.com' + href

    def video_is_duplicate(self, next_video_html):
        next_link = self.make_link_from_html(next_video_html)
        #check if next_link is found in self.videos
        if any(v['link'] == next_link for v in self.videos):
            print(f"{next_link} is a duplicate \n Retrying ...")
            return True
        else:
            return False
    
    def video_is_youtube_movie(self, next_video_html): 
        next_video_html_subtext = next_video_html.find('span', class_='')
        
        if next_video_html_subtext and next_video_html_subtext.text == "YouTube Movies":
            print("next video html is for a YouTube Movie")
            return True
        else:
            return False

    def pick_next_video_html_from_list(self, soup):
        next_video_html_list = self.find_next_video_html_list(soup)
            
        for i in range(1, len(next_video_html_list)):
            new_html = next_video_html_list[i]
            new_html_is_youtube_movie = self.video_is_youtube_movie(new_html)
            new_html_is_duplicate = self.video_is_duplicate(new_html)

            if not new_html_is_duplicate and not new_html_is_youtube_movie:
                return new_html
            else:
                print("New next video html is not valid. Retrying ...")
        
        print("Could not find valid next video html from list")

class VideoData:
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
            category_title = self.soup.find('h4', class_='title', text = re.compile('Category'))
            #Find category value from parent
            parent = category_title.parent
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
        dives = 30
        test = RabbitHole(examples[key], dives)
        test.save_json(name=f"{key}-{dives}")