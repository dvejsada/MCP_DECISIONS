import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


def get_supreme_admin_court_decision(case_number):
    # URL encode the file_number
    encoded_file_number = quote_plus(case_number)

    # Construct the search URL using only 'oznacenivecivcelku'
    search_url = (
        'https://vyhledavac.nssoud.cz/'
        f'?teaserFilledSearch='
        f'AND:oznacenivecidelenesenat:|'
        f'AND:oznacenivecidelenerejstrikovaznackaSID:|'
        f'AND:oznacenivecideleneporadovecislo:|'
        f'AND:oznacenivecidelenerok:|'
        f'AND:oznacenivecidelenecislojednaci:|'
        f'AND:oznacenivecivcelku:"{encoded_file_number}"'
    )

    # Send a GET request to the search URL using httpx
    response = httpx.get(search_url)
    response.encoding = 'utf-8'  # Ensure correct encoding
    search_html = response.text

    # Parse the search HTML to find the link to the decision text
    search_soup = BeautifulSoup(search_html, 'html.parser')

    # Initialize the dictionary to store the data
    decision_data = {}

    # Find the table containing the search results
    table = search_soup.find('table', {'id': 'tresults'})
    if not table:
        return 'No Supreme Administrative Court decision with such case number was found.'

    tbody = table.find('tbody')
    if not tbody:
        return 'No Supreme Administrative Court decision with such case number was found.'

    row = tbody.find('tr')
    if not row:
        return 'No Supreme Administrative Court decision with such case number was found.'

    # Extract data from the table cells
    cells = row.find_all('td')
    if len(cells) >= 11:
        decision_data['date_of_decision'] = cells[2].get_text(strip=True)
        decision_data['case_number'] = cells[3].get_text(strip=True)
        decision_data['type_of_decision'] = cells[5].get_text(strip=True)
        decision_data['outcome'] = cells[6].get_text(strip=True)
        decision_data['parties'] = cells[9].get_text(strip=True)

        # Find the link to the decision text
        links = cells[10].find_all('a')
        decision_text_link = None
        for link in links:
            href = link.get('href')
            if 'DokumentOriginal/Text/' in href:
                decision_text_link = 'https://vyhledavac.nssoud.cz' + href
                break

        decision_pdf_link = None
        for link in links:
            href = link.get('href')
            if 'DokumentOriginal/Index/' in href:
                decision_pdf_link = 'https://vyhledavac.nssoud.cz' + href
                break

        if decision_pdf_link:
            decision_data['link_to _decision'] = decision_pdf_link
        else:
            decision_data['link_to _decision'] = "No link is available"

        if decision_text_link:
            # Send a GET request to the decision text URL using httpx
            decision_response = httpx.get(decision_text_link)
            decision_response.encoding = 'utf-16-le'  # Ensure correct encoding
            decision_html = decision_response.text

            # Parse the decision HTML
            decision_soup = BeautifulSoup(decision_html, 'html.parser')

            # Extract the text of the decision
            body = decision_soup.find('body')

            if body:
                text = body.get_text(separator='\n')
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                decision_text = '\n'.join(lines)
                decision_text = decision_text.replace('\x00', '')
                decision_data['decision_text'] = decision_text
            else:
                decision_data['decision_text'] = 'Decision text not found.'
        else:
            decision_data['decision_text'] = 'Decision text link not found.'

        return decision_data
    else:
        return "Failed to extract data from the webpage."
