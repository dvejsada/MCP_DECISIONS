import httpx
from bs4 import BeautifulSoup

def check_case_no(case_no: str) -> bool:
    """Validates case number"""

    if "ÚS" not in case_no:
        return False

    if "/" not in case_no:
        return False

    return True

def check_not_empty(data) -> bool:
    """Check if there is any content in 'DocContent' cell"""

    soup = BeautifulSoup(data, 'html.parser')
    td = soup.find('td',attrs={"class":"DocContent"})

    if td:
        table = td.find('table')
        if table:
            row = table.get_text(separator="", strip=True)
            if row:
                return True  # Table is not empty
    return False # Table is empty or does not exist

def extract_decision_text(data) -> tuple[str,str]:
    """Extracts text of the decision"""
    soup = BeautifulSoup(data, 'html.parser')
    td_content = soup.find('td', attrs={"class": "DocContent"})
    if td_content:
        table = td_content.find('table')
        if table:
            row = table.find('tr')
            decision_text = row.get_text(separator=' ', strip=True)
        else:
            decision_text = "No decision text found."
    else:
        decision_text = "No decision text found."

    span_registry = soup.find('span', attrs={"class": "DocRegistrySign"})
    if span_registry:
        registry = span_registry.get_text(separator=' ', strip=True)
    else:
        registry = "Not found."

    return decision_text, registry


def extract_abstract_text(data) -> str:
    """Extract abstract of the decision"""

    soup = BeautifulSoup(data, 'html.parser')
    abstract_table = soup.find('table', attrs={"class": "abstractContent"})
    if abstract_table:
        abstract_text = abstract_table.get_text(separator=' ', strip=True)
    else:
        abstract_text = "No abstract found."

    legal_sentence_table = soup.find('table', attrs={"class": "legalSentenceContent"})
    if legal_sentence_table:
        legal_sentence_text = legal_sentence_table.get_text(separator=' ', strip=True)
    else:
        legal_sentence_text = "No legal sentence text found."

    formatted_text = (f"Abstrakt: {abstract_text}\n"
                      f"Právní věta: {legal_sentence_text}")

    return formatted_text


def get_constitutional_court_decision(case_no: str) -> str:
    """Return text of the constitutional court decision based on case number."""

    if check_case_no(case_no):

        split_case_no: list = case_no.split(".")
        further_split = split_case_no[1].split(" ")
        docket_year = further_split[-1].split("/")

        senate_no = split_case_no[0]
        docket_no = docket_year[0]
        year_no = docket_year[1]

        doc_no = 3

        for i in range(doc_no):
            case_url = f"https://nalus.usoud.cz/Search/GetText.aspx?sz={senate_no}-{docket_no}-{year_no}_{doc_no}"
            response = httpx.get(url=case_url)

            if response.status_code == 200:
                if check_not_empty(response.text):
                    print(f"Found non-empty decision under {doc_no}")
                    decision_text, case_citation = extract_decision_text(response.text)
                    abstract_response = httpx.get(url=f"https://nalus.usoud.cz/Search/GetAbstract.aspx?sz={senate_no}-{docket_no}-{year_no}_{doc_no}")
                    abstract_text = extract_abstract_text(abstract_response.text)
                    break
                doc_no = doc_no - 1
                if doc_no == 0:
                    return "No decision found"

        formatted_text = (f"Spisová značka: {case_citation}\n"
                          f"Odkaz na rozhodnutí: {case_url}\n"
                          f"{abstract_text}\n"
                          f"***\n"
                          f"Text rozhodnutí:\n"
                          f"{decision_text}")

        return formatted_text

    else:
        return "The provided case number in not valid Constitutional court case number."
