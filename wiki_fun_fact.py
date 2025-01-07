import requests
import random
import pyfiglet
import sys
import os


def display_image(image_url):
    """
    Display an image in the terminal using supported tools: `kitty +kitten icat`, `viu`, or `w3m`.
    """
    image_path = "thumbnail.jpg"

    response = requests.get(
        image_url,
        headers={
            "User-Agent": "wiki-fun-fact-bot/1.0 (https://www.sammorris.ca; dodobird181@gmail.com)"
        },
        stream=True,
    )
    if response.status_code == 200:
        with open(image_path, "wb") as f:
            f.write(response.content)

        try:
            # Try displaying the image
            if os.system("kitty +kitten icat thumbnail.jpg") == 0:
                return
            elif os.system("viu thumbnail.jpg") == 0:
                return
            elif os.system("w3m thumbnail.jpg") == 0:
                return
            else:
                print(
                    "Image display tools not found. Saved the image as 'thumbnail.jpg'."
                )

        except Exception as e:
            print(f"Failed to display image: {e}")

        finally:
            try:
                os.remove("thumbnail.jpg")
            except FileNotFoundError:
                # clean-up failed.. might have never made a mess in the first place!
                ...

    else:
        print("Failed to download the image.")


def get_random_article_from_categories(*categories):

    # collect unique category members
    api_url = "https://en.wikipedia.org/w/api.php"
    all_category_members = []
    for category in categories:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "format": "json",
            # get as many pages as possible
            "cmlimit": "max",
        }
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            print("Error fetching category members.")
            return None
        data = response.json()
        for member in data.get("query", {}).get("categorymembers", []):
            all_category_members.append(member)
    if not all_category_members:
        # exit if no members found across any category!
        print(f"No articles found in any category: {categories}")
        return None
    unique_members = []
    unique_titles = []
    for member in all_category_members:
        if member["title"] not in unique_titles:
            if "CATEGORY" not in member["title"].upper():
                # prevent sub-categories of categories from being included... too complicated!
                unique_members.append(member)
                unique_titles.append(member["title"])

    random_page = random.choice(unique_members)
    page_title = random_page["title"]
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
    summary_response = requests.get(summary_url)

    if summary_response.status_code != 200:
        print(f"Error fetching summary for page: {page_title}")
        return None

    summary_data = summary_response.json()
    title = summary_data.get("title", "No title available")
    extract = summary_data.get("extract", "No summary available")
    image_url = summary_data.get("thumbnail", {}).get(
        "source", None
    )  # Get thumbnail URL

    return title, extract, image_url


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Please enter the wikipedia categories you wish to receive fun-facts for, separated "
            + 'by a space. E.g., "Gardening Mythology Coffee".'
        )
        exit(1)
    no_image = False
    if "--no-image" in sys.argv:
        sys.argv.remove("--no-image")
        no_image = True
    categories = sys.argv[1:]
    result = get_random_article_from_categories(*categories)

    if result:
        title, summary, image_url = result
        print(pyfiglet.figlet_format(title))
        print(summary)
        if image_url and not no_image:
            display_image(image_url)
