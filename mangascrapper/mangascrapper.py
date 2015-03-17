#!/usr/bin/env python

import os
import re
import logging
import argparse
import tarfile
import zipfile
from enum import Enum

from natsort import natsorted
import simplejson
from lxml import html
from reportlab.lib.pagesizes import A2
from reportlab.platypus import SimpleDocTemplate, Image
import requests
import requests.adapters
import requests.exceptions


__author__ = 'Psycho_Coder'
__version__ = '1.2'

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
          Version : 1.2

A tool to download manga's and save them in
a directory and as well as save them as an
ebook in pdf format.
"""


class OutFormats(Enum):
    CBR = "cbr"
    CBZ = "cbz"
    CBT = "cbt"
    PDF = "pdf"


class MangaScrapper():
    def __init__(self, manga_name, begin, end, storage_loc, latest=False, outformat=OutFormats.PDF):
        """
        Constructor to initialize the requirements and variables to download manga.

        :param outformat: Output Format of the Manga in either PDF/CBR/CBZ/CBT
        :param latest: If true downloads the latest manga chapter.
        :type latest: bool
        :param manga_name: Name of the Manga to be downloaded
        :param begin: Manga chapter from which the download will start.
        :param end: Manga chapter after which the download will stop.
        :param storage_loc: Directory Location to store the downloaded Manga.
        """
        print("Pre-processing Requirements...")
        print("Building up indexes...")

        manga_url = "http://www.mangapanda.com/" + self.todashcase(manga_name) + "/"

        self.__outformat__ = outformat
        self.__resp_obj__ = None
        self.__json_data__ = simplejson.loads(str(requests.get("http://www.mangapanda.com/actions/selector/",
                                                               params={"id": self._get_mangaid_(manga_url + "1"),
                                                                       "which": 191919}).text))
        print("Building indexes and tables - Done")

        if latest:
            begin, end = len(self.__json_data__), len(self.__json_data__)
            print("\nDownloading the latest manga chapter..")
            logging.info("Latest Manga Chapter will be downloaded.")
        elif (begin or end) is None:
            begin, end = 1, len(self.__json_data__)
            print("\nAttempting to download the complete manga.")
            logging.info("Specific chapters not downloaded. Complete Manga will be downloaded.")

        self.__Constants__ = {
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
        text = "".join([c for c in text if c not in "().*&;"])
        return text.strip().replace(" ", "-").lower()

    def start_scrapping(self):
        """
        Method that performs the crawling and saving the manga chapters and also
        directs the output format of the manga chapter book.
        """
        save_loc = self.__Constants__['manga_save_loc']
        chap, begin, end = 1, self.__Constants__['begin'], self.__Constants__['end']
        end_message = """
            All the Chapters Requested has been downloaded.
            Manga Saved in : {0}

            Thank you! For Using MangaScrapper. If you Like this tool please
            consider donating or Flattr this Project.
        """.format(save_loc)

        print(title)
        print("Manga To be Downloaded :- " + self.__Constants__['manga_name'])
        print("Manga Output Format :- " + str(self.__outformat__.value).upper())
        logging.info("Manga To be Downloaded :- " + self.__Constants__['manga_name'])

        if not os.path.exists(save_loc):
            os.mkdir(save_loc)
            print("Manga to be stored in : " + save_loc)
            logging.info("Manga to be stored in : " + save_loc)
        else:
            logging.warning("The Manga download directory exists and further chapters "
                            "to be saved there.")

        for chap in range(begin, end + 1):

            chap_url = self.__Constants__['manga_url'] + str(chap)
            chapname = self.__json_data__[chap - 1]['chapter_name']

            if chapname == "":
                chapname = self.__Constants__['manga_name'] + " - Chapter " + str(chap)
            else:
                chapname = self.__Constants__['manga_name'] + " - Chapter {0} - {1}".\
                    format(str(chap), self.__json_data__[chap - 1]['chapter_name'])

            chap_save_loc = os.path.join(save_loc, chapname)

            if not os.path.exists(chap_save_loc):
                os.mkdir(chap_save_loc)
            else:
                logging.warning("The Manga Chapter directory exists and further chapters "
                                "to be saved there.")
            print("\n\t[+] Downloading Chapter {0} : {1}".format(str(chap), chapname))

            no_of_pages = self._get_chapter_pagecount_(chap_url)
            page = 1

            while page <= no_of_pages:
                img_save_loc = os.path.join(chap_save_loc, str(page) + ".jpg")
                errorocc = False
                if not os.path.exists(img_save_loc):
                    img_url = self._get_page_img_url_(chap_url + "/" + str(page))
                    self._set_response_ins_(img_url)

                    if self.__resp_obj__.status_code == 503:
                        errorocc = True

                    if not errorocc:
                        with open(img_save_loc, "wb") as f:
                            f.write(self.__resp_obj__.content)
                        print("\t\t[-] Page {0} Image Saved as {1}".format(page, str(page) + ".jpg"))
                    else:
                        page -= 1
                else:
                    logging.warning("\t[-] Page {0} Image exists and therefore skipping "
                                    "{1}".format(page, str(page) + ".jpg"))
                page += 1

            self._create_comic_file_(chap_save_loc, self.__outformat__)

        if chap == end:
            print(end_message)
        else:
            logging.error("\tUnable to download the requested Manga chapters. Try Again!", logging.ERROR)

    def _set_response_ins_(self, pageurl):
        """
        Sets the response for the GET request of pageurl and stores it in self.resp
        :param pageurl: url for which we store the response.
        """
        try:
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=5)
            s.mount('http://', a)
            resp = s.get(pageurl, timeout=30)
            self.__resp_obj__ = resp
            resp.close()
        except requests.exceptions.Timeout:
            logging.error("\tVery Slow Internet Connection.", logging.ERROR)
        except requests.exceptions.ConnectionError:
            logging.error("\tNetwork Unavailable. Check your connection.", logging.ERROR)
        except requests.exceptions.MissingSchema:
            logging.error("\t503 Service Unavailable. Retrying download ... ", logging.ERROR)

    def _get_chapter_pagecount_(self, chapurl):
        """
        Returns the # of Pages in a particular chapter.
        :param chapurl: Chapter URL from which the # of Pages to be retrieved.
        :return: # of Pages in a chapter
        :rtype: int
        """
        self._set_response_ins_(chapurl)
        pagedata = html.fromstring(self.__resp_obj__.content)
        return int(pagedata.xpath(self.__Constants__["lastpage_xpath"])[0])

    def _get_mangaid_(self, page_url):
        """
        Returns the mangaid for a specific Manga.
        :param page_url: Page URL from which mangaid to be retrieved/
        :return: Returns Manga ID.
        :rtype: int
        """
        mangaid_pat = r"document\[\'mangaid\'\] = [0-9]{0,};"
        self._set_response_ins_(page_url)
        match = re.search(mangaid_pat, self.__resp_obj__.text)
        return int(match.group().split("=")[1].strip().split(";")[0])

    def _get_page_img_url_(self, page_url):
        """
        Returns the image url in a page of a particular chapter in Manga.
        :param page_url: Page URL from which the image url is to be downloaded.
        :return: Returns URL of the image in page_url.
        :rtype: str
        """
        try:
            self._set_response_ins_(page_url)
            pagedata = html.fromstring(self.__resp_obj__.content)
            return str(pagedata.xpath(self.__Constants__['img_xpath'])[0])
        except IndexError:
            pass

    def _correct_img_size_(self, imgpath):
        pass

    def _create_comic_file_(self, chap_save_loc, comic_format):
        chapname = os.path.basename(chap_save_loc)

        if self.__outformat__ == OutFormats.PDF:
            img_list = natsorted(os.listdir(chap_save_loc))
            pdf_save_loc = chap_save_loc + ".pdf"
            doc = SimpleDocTemplate(pdf_save_loc, pagesize=A2)
            parts = [Image(os.path.join(chap_save_loc, img)) for img in img_list]

            try:
                doc.build(parts)
            except PermissionError:
                logging.error("Missing Permission to write. File open in system editor or missing "
                              "write permissions.", logging.ERROR)
        elif comic_format == OutFormats.CBR:
            cbr_save_loc = chap_save_loc
            self._create_cbz_(cbr_save_loc, chapname + ".cbr")
        elif comic_format == OutFormats.CBZ:
            cbr_save_loc = chap_save_loc
            self._create_cbz_(cbr_save_loc, chapname + ".cbz")
        elif comic_format == OutFormats.CBT:
            cbr_save_loc = chap_save_loc
            self._create_cbt_(cbr_save_loc, chapname + ".cbt")

    @staticmethod
    def _create_cbz_(dirpath, archivename):
        """

        :param dirpath:
        :param archivename:
        """
        currdir = os.getcwd()
        try:
            import zlib

            compression = zipfile.ZIP_DEFLATED
        except ImportError:
            logging.warning("zlib library not available. Using ZIP_STORED compression.")
            compression = zipfile.ZIP_STORED
        try:
            with zipfile.ZipFile(archivename, "w", compression) as zf:
                os.chdir(os.path.abspath(os.path.join(dirpath, os.pardir)))
                name = os.path.basename(dirpath)
                for file in os.listdir(name):
                    zf.write(os.path.join(name, file))
        except zipfile.BadZipfile:
            logging.error("Unable to compile CBR file ", logging.ERROR)
        os.chdir(currdir)

    @staticmethod
    def _create_cbt_(dirpath, archivename):
        """

        :param dirpath:
        :param archivename:
        """
        try:
            with tarfile.open(archivename, "w") as tar:
                tar.add(dirpath, arcname=os.path.basename(dirpath))
        except tarfile.TarError:
            logging.error("Unable to create CBT file. Report to Developer.", logging.ERROR)


def check_negative(value):
    """
    Checks for Negative values in arguments.
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
    desc = "MangaScrapper is simple, easy, and fast CLI tool to download manga's " \
           "and also create an ebook in pdf format."

    parser = argparse.ArgumentParser(description=desc, prog="mangascrapper.py")
    parser.add_argument('manga_name', type=str, help="Enter the name of the manga.")
    parser.add_argument('-b', '--begin', type=check_negative,
                        help="Enter the starting chapter. By default its first chapter")
    parser.add_argument('-e', '--end', type=check_negative,
                        help="Enter the ending chapter. Defaults to the last chapter "
                             "possible.")
    parser.add_argument('-c', '--chapter', type=check_negative,
                        help="Give the chapter number if you want to download only "
                             "one chapter.")
    parser.add_argument('-l', '--location', type=str, help="The location where manga has "
                                                           "to be downloaded. By default stored in the current directory.",
                        default=os.getcwd())
    parser.add_argument('-lc', '--latest', action='store_true', help="Download the latest Manga chapter")
    parser.add_argument('-out', '--outformat', type=str, help="Generated Manga/Comic book output formats. Available "
                                                              "formats are cbr, cbz, cbt, & pdf; default is pdf.",
                        default="pdf")

    args = parser.parse_args()

    if args.chapter and (args.begin or args.end):
        print("--chapter argument cannot be used along with --begin/--end. \n")
        parser.parse_args(["--help"])
    elif args.chapter and args.latest:
        print("--chapter argument cannot be used along with --latest \n")
        parser.parse_args(["--help"])
    elif args.latest and (args.begin or args.end):
        print("--latest argument cannot be used along with --begin/--end. \n")
        parser.parse_args(["--help"])
    else:
        if args.location and not os.path.isdir(args.location):
            raise OSError("The given save location is not valid. It must be a directory.")
        elif not os.access(args.location, os.W_OK):
            raise OSError("You do not have permission to write in the given path. Run as root.")

        if args.outformat.strip().lower() == "cbr":
            args.outformat = OutFormats.CBR
        elif args.outformat.strip().lower() == "cbz":
            args.outformat = OutFormats.CBZ
        elif args.outformat.strip().lower() == "cbt":
            args.outformat = OutFormats.CBT
        else:
            args.outformat = OutFormats.PDF

        if args.latest:
            scrape = MangaScrapper(args.manga_name, args.chapter, args.chapter, args.location, latest=True,
                                   outformat=args.outformat)
        elif args.chapter:
            scrape = MangaScrapper(args.manga_name, args.chapter, args.chapter, args.location, outformat=args.outformat)
        else:
            scrape = MangaScrapper(args.manga_name, args.begin, args.end, args.location, outformat=args.outformat)

        scrape.start_scrapping()


if __name__ == "__main__":
    main()