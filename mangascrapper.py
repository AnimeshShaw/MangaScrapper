import json
import os
import re
import logging
from lxml import html
import argparse

from reportlab.lib.pagesizes import A2
from reportlab.platypus import SimpleDocTemplate, Image
import requests
import requests.adapters
import requests.exceptions

__author__ = 'Psycho_Coder'

title = """
  __  __
 |  \/  | __ _ _ __   __ _  __ _
 | |\/| |/ _` | '_ \ / _` |/ _` |
 | |  | | (_| | | | | (_| | (_| |
 |_|  |_|\__,_|_| |_|\__, |\__,_|
  ____               |___/
 / ___|  ___ _ __ __ _ _ __  _ __   ___ _ __
 \___ \ / __| '__/ _` | '_ \| '_ \ / _ \ '__|
  ___) | (__| | | (_| | |_) | |_) |  __/ |
 |____/ \___|_|  \__,_| .__/| .__/ \___|_|
                      |_|   |_|

                      By : Psycho_Coder
          rC Developers @ rawCoders.com

A tool to download manga's and save them in
a directory and as well as save them as an
ebook in pdf format.
"""


class MangaScrapper():
    def __init__(self, manga_name, begin, end, storage_loc):
        """
        Constructor to initialize the requirements and variables to download manga.

        :param manga_name: Name of the Manga to be downloaded
        :param begin: Manga chapter from which the download will start.
        :param end: Manga chapter after which the download will stop.
        :param storage_loc: Directory Location to store the downloaded Manga.
        """
        print("Pre-processing Requirements...")
        print("Building up indexes...")

        manga_url = "http://www.mangapanda.com/" + self.todashcase(manga_name) + "/"
        self.resp_data = ""
        self.json_data = json.loads(str(requests.get("http://www.mangapanda.com/actions/selector/",
                                                     params = { "id": self._get_mangaid_(manga_url + "1"),
                                                                "which": 191919 }).text))

        print("Building indexes and tables - Done")

        if (begin or end) is None:
            begin, end = 1, len(self.json_data)
            print("\nAttempting to download the complete manga.")
            logging.info("Specific chapters not downloaded. Complete Manga will be downloaded.")

        self.Constants = {
            "manga_name": manga_name,
            "begin": begin,
            "end": end,
            "base_url": "http://www.mangapanda.com",
            "manga_url": manga_url,
            "img_xpath": ".//img[@id='img']/@src",
            "lastpage_xpath": ".//*[@id='pageMenu']/option[last()]/text()",
            "manga_save_loc": os.path.join(storage_loc, manga_name),
        }

        logging.info("Building the Data Table - Done")

    @staticmethod
    def todashcase(text):
        """
        Change Sentences to lowercase and words separated by '-'
        :param text: String to convert to dash case.
        :type text: str
        :return Returns String in dash case.
        """
        return text.strip().replace(" ", "-").lower()

    def start_scrapping(self):
        print(title)

        save_loc = self.Constants['manga_save_loc']
        begin, end = self.Constants['begin'], self.Constants['end']

        print("Manga To be Downloaded :- " + self.Constants['manga_name'])
        logging.info("Manga To be Downloaded :- " + self.Constants['manga_name'])

        if not os.path.exists(save_loc):
            os.mkdir(save_loc)
            print("Manga to be stored in : " + save_loc)
        else:
            logging.warn("The Manga download directory exists and further chapters "
                         "to be saved there.")
            pass

        for chap in xrange(begin, end + 1):
            chap_url = self.Constants['manga_url'] + str(chap)
            chapname = self.json_data[chap - 1]['chapter_name']

            if chapname == "":
                chapname = "Chapter " + str(chap)
            else:
                chapname = "Chapter {0} - {1} ".format(str(chap), self.json_data[chap - 1]['chapter_name'])

            chap_save_loc = os.path.join(save_loc, chapname)

            if not os.path.exists(chap_save_loc):
                os.mkdir(chap_save_loc)
            else:
                logging.warn("The Manga Chapter directory exists and further chapters "
                             "to be saved there.")
                pass

            no_of_pages = self._get_chapter_pagecount_(chap_url)

            print("\n\t[+] Downloading Chapter {0} : {1}".format(str(chap), chapname))

            pdf_save_loc = os.path.join(save_loc, chapname + ".pdf")
            doc = SimpleDocTemplate(pdf_save_loc, pagesize = A2)
            parts = []

            for page in xrange(1, no_of_pages + 1):

                img_save_loc = os.path.join(chap_save_loc, str(page) + ".jpg")

                if not os.path.exists(img_save_loc):
                    img_url = self._get_page_img_url_(chap_url + "/" + str(page))
                    self.store_response_data(img_url)

                    with open(img_save_loc, "wb") as f:
                        f.write(self.resp_data)
                        parts.append(Image(img_save_loc))
                    print("\t\t[-] Page {0} Image Saved as {1}".format(page, str(page) + ".jpg"))
                else:
                    parts.append(Image(img_save_loc))
                    pass

            doc.build(parts)
            end_message = """
                        All the Chapters Requested has been downloaded.
                        Manga Saved in : {0}

                        Thank you! For Using MangaScrapper. If you Like this tool please
                        consider donating or Flattr this Project.
            """.format(save_loc)
            print(end_message)

    def store_response_data(self, pageurl):
        resp = ""
        try:
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries = 5)
            s.mount('http://', a)
            resp = s.get(pageurl, timeout = 30)
            self.resp_data = resp.content
        except requests.exceptions.Timeout:
            print("Very Slow Internet Connection.")
            logging.error("Very Slow Internet Connection.")
        except requests.exceptions.ConnectionError:
            print("Network Unavailable. Check your connection.")
            logging.error("Network Unavailable. Check your connection.")
        except requests.exceptions.MissingSchema:
            logging.error("Problem with connection. Retrying ... ")
            self.store_response_data(pageurl)
        resp.close()

    def _get_chapter_pagecount_(self, chapurl):
        """
        Returns the # of Pages in a particular chapter.
        :param chapurl: Chapter URL from which the # of Pages to be retrieved.
        :return: # of Pages in a chapter
        :rtype: int
        """
        self.store_response_data(chapurl)
        pagedata = html.fromstring(self.resp_data)
        return int(pagedata.xpath(self.Constants["lastpage_xpath"])[0])

    def _get_mangaid_(self, page_url):
        """
        Returns the mangaid for a specific Manga.
        :param page_url: Page URL from which mangaid to be retrieved/
        :return: Returns Manga ID.
        :rtype: int
        """
        mangaid_pat = r"document\[\'mangaid\'\] = [0-9]{0,};"
        self.store_response_data(page_url)
        match = re.search(mangaid_pat, self.resp_data)
        return int(match.group().split("=")[1].strip().split(";")[0])

    def _get_page_img_url_(self, page_url):
        """
        Returns the image url in a page of a particular chapter in Manga.
        :param page_url: Page URL from which the image url is to be downloaded.
        :return: Returns URL of the image in page_url.
        :rtype: str
        """
        url = page_url
        try:
            self.store_response_data(page_url)
            pagedata = html.fromstring(self.resp_data)
            return str(pagedata.xpath(self.Constants['img_xpath'])[0])
        except IndexError:
            self._get_page_img_url_(url)


def check_negative(value):
    """
    Checks for Negetive values in arguments.
    :param value: Value whose positive nature is checked.
    :return:
    :rtype: int
    :raise argparse.ArgumentTypeError:
    """
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def main():
    """
    Main Method and UI/CLI for the MangaScrapper.

    :raise OSError:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('manga_name', type = str, help = "Enter the name of the manga.")
    parser.add_argument('-b', '--begin', type = check_negative,
                        help = "Enter the starting chapter. By default its first chapter")
    parser.add_argument('-e', '--end', type = check_negative,
                        help = "Enter the ending chapter. Defaults to the last chapter "
                               "possible.")
    parser.add_argument('-c', '--chapter', type = check_negative,
                        help = "Give the chapter number if you want to download only "
                               "one chapter.")
    parser.add_argument('-l', '--location', type = str, help = "The location where manga has "
                        "to be downloaded. By default stored in the current directory.",
                        default = os.getcwd())

    args = parser.parse_args()

    if args.chapter and (args.begin or args.end):
        print("--chapter argument cannot be used along with --begin/--end. \n")
        parser.parse_args(["--help"])
    else:
        if args.location and not os.path.isdir(args.location):
            raise OSError("The given save location is not valid. It must be a directory.")
        elif not os.access(args.location, os.W_OK):
            raise OSError("You do not have permission to write in the given path. Run as root.")

        if args.chapter:
            scrape = MangaScrapper(args.manga_name, args.chapter, args.chapter, args.location)
        else:
            scrape = MangaScrapper(args.manga_name, args.begin, args.end, args.location)

        scrape.start_scrapping()


if __name__ == "__main__":
    main()