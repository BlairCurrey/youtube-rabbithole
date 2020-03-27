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
        
        #Find new video html and soup if first attempt yields None
        if next_video_html is None:
            next_video_html, video["soup"] = self.retry_find_next_video_html(video["soup"], video["link"], next_video_html)
        
        # Make link
        video['next_link'] = self.make_link_from_html(next_video_html)

        #Find new video if video is a duplicate
        if self.video_is_duplicate(video['next_link']):
            video['next_link'] = self.find_non_duplicate_video(video["soup"])
        
        #get the rest of the data
        scraped_video = Video_data(video['link'], video['next_link'], video["soup"], video['id'])

        print(scraped_video.data)
        return scraped_video.data
    
    def get_soup(self, current_video):
        # Get web page
        page = requests.get(current_video)
        
        # Print status code for debugging purposes
        print(f"[{len(self.videos) + 1}] Request status code for {current_video}: {str(page.status_code)}")
        
        # Parse HTML
        return BeautifulSoup(page.content, 'html.parser')

    def find_next_video_html(self, soup, retry_with_new_soup=False):
            return soup.find('a', class_='content-link')

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
    
    def find_next_video_html_list(self, soup):
        return soup.find_all('a', class_='content-link')
    
    def make_link_from_html(self, validated_html):
        href = validated_html.get('href')
        return 'https://www.youtube.com' + href

    def video_is_duplicate(self, next_link):
        #check if next_link is found in self.videos
        if any(v['link'] == next_link for v in self.videos):
            print(f"{next_link} is a duplicate \n Retrying ...")
            return True
        else:
            return False

    def find_non_duplicate_video(self, soup):
        next_video_html_list = self.find_next_video_html_list(soup)
            
        # make a new possible link from the list of videos (skipping the first video that we already tried)
        for item in range(1, len(next_video_html_list)):
            # possible_new_link = 'https://www.youtube.com' + videos_html[i].get('href')
            possible_new_link = self.make_link_from_html(next_video_html_list[item]) 
            possible_new_link_is_duplicate = self.video_is_duplicate(possible_new_link)

            # #if the new possible link has not been visited, make it the next video
            if not possible_new_link_is_duplicate:
                print(f"found new valid link: {possible_new_link}")
                return possible_new_link
            else:
                print(f"Possible new link ({possible_new_link}) is a duplicate. Retrying...")

        print(f"Could not find new link that was not a duplicate from: \n {next_video_html_list}")

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
        dives = 10
        test = Rabbithole(examples[key], dives)
        test.save_json(name=f"{key}-{dives}")