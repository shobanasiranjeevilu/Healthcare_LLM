
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


def clean_symptoms_text(symptoms_text):
    # Remove HTML tags
    cleaned_text = re.sub(r'<[^>]+>', '', symptoms_text)
    cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text)
    cleaned_text = ' '.join(cleaned_text.split())
    return cleaned_text


def split_symptoms(cleaned_text):
    symptoms_list = cleaned_text.split(', ')
    return symptoms_list 
    
def extract_signs_and_symptoms(signs_and_symptoms_heading):
    if signs_and_symptoms_heading:
        content = []
        parent_h2 = signs_and_symptoms_heading.find_parent('h2')
        if parent_h2 is None:
            return ''
        for elem in parent_h2.find_next_siblings():
            # Stop if we hit another <h2> tag (the next section)
            if elem.name == "h2":
                break
            if elem.name == "p":
                # Collect the text of the first <p> tag
                content.append(elem.get_text(separator=" ", strip=True))
                break

        
        symptoms_text = ' '.join(content)
        symptoms = split_symptoms(clean_symptoms_text(symptoms_text))
        
        return symptoms



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
                signs_and_symptoms_heading = soup.find(id="Signs_and_symptoms")
                
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
                            
                if signs_and_symptoms_heading is not None and disease not in diseases_with_symptoms.keys():
                    
                    symptom = extract_signs_and_symptoms(signs_and_symptoms_heading)
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


