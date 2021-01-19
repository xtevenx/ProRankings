import urllib.request
import xml.etree.ElementTree
import zipfile

if __name__ == "__main__":
    print("Downloading data file ... ")
    url = "http://ratings.fide.com/download/players_list_xml.zip"
    urllib.request.urlretrieve(url, "players_list_xml.zip")

    print("Extracting data file ... ")
    with zipfile.ZipFile("players_list_xml.zip", "r") as data_file:
        data_file.extractall()

    print("Processing data file ... ")
    tree = xml.etree.ElementTree.parse("players_list_xml_foa.xml")
    root = tree.getroot()

    print("Calculating the average rating ... ")
    total_rating, num_ratings = 0, 0
    for player_data in root:
        for attribute in player_data:
            if attribute.tag == "rating" and attribute.text is not None:
                total_rating += int(attribute.text)
                num_ratings += 1

    print(f"Average rating: {total_rating / num_ratings:.2f}")
