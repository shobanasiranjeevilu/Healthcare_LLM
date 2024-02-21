
import re
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")



def search_wikipedia_for_url(search_term):

    endpoint = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search_term
    }
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        if search_results:
            return search_results
        
    


def web_scrape_wikipedia(disease_list):

    """
    disease_list: input list takes list of disease to search and collect the symptoms from wikipedia
    diseases_with_symptoms: Returns dictionary containing diseases and its symptoms
    """
    diseases_with_symptoms = {}
    for disease in disease_list:
        url_link = search_wikipedia_for_url(disease)
        
        if url_link:
            for url in url_link:

                page_title = url['title']

                page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                
                wiki = requests.get(page_url, verify=False)
                soup = BeautifulSoup(wiki.content, 'html5lib')
                info_table = soup.find("table", {"class": "infobox"})
                if info_table:
                    for row in info_table.find_all("tr"):
                        header = row.find("th", {"scope": "row"})
                        if header and header.get_text() == "Symptoms":
                            symptom = row.find("td")
                            if symptom:
                                
                                symptom = ' '.join(re.sub(r'<.*?>|\[.*?\]', ' ', str(symptom)).split())
                                diseases_with_symptoms[disease] = []
                                diseases_with_symptoms[disease].append(page_title)
                                diseases_with_symptoms[disease].append(symptom)

                if disease in diseases_with_symptoms.keys():
                    break

    return diseases_with_symptoms


def get_disease_url(base_url, disease):

    # Get list of disease's links from A-Z page
    url = base_url + '/conditions/a-z/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    for link in soup.find_all('option'):
        if link.text == disease:
            return link.get('value')


def web_scrape_seattle_children(base_url, unretirved_diseases):

    unretirved_diseases_symptoms = {}
    for disease in unretirved_diseases:

        url = get_disease_url(base_url, disease)
        if url:
            page = requests.get(base_url + url)
            soup = BeautifulSoup(page.content, 'html.parser')

            headings = soup.find_all(re.compile('h[1-6]'), text=re.compile('.*Symptom.*'))
            for h in headings:
                ul = h.find_next('ul')
                if ul:
                    symptoms = [li.text for li in ul.find_all('li')]
                    unretirved_diseases_symptoms[disease] = []
                    unretirved_diseases_symptoms[disease].append(disease)
                    unretirved_diseases_symptoms[disease].append(symptoms)

    return unretirved_diseases_symptoms


