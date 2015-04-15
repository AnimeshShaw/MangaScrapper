from lxml.html import parse

__author__ = 'Psycho_Coder'


def main():
    with open("mangalist.csv", "w") as f:
        tree = parse("http://www.mangapanda.com/alphabetical")
        manga_name_list = tree.xpath("//ul[@class='series_alpha']/li/a/text()")
        manga_url_list = tree.xpath("//ul[@class='series_alpha']/li/a/@href")
        f.write("\"Manga Name\", URL\n")

        for i in range(len(manga_name_list)):
            f.write("\"{0}\", http://www.mangapanda.com{1}\n".format(manga_name_list[i].replace("\"", ""), manga_url_list[i]))

if __name__ == "__main__":
    main()
