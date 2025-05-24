import httpx
import pandas as pd
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class ActProposals:

    def __init__(self):
        self.timestamp = None
        self.url = "https://www.psp.cz/sqw/tisky.sqw?tqb1=1&utq=2&o=9&tqb2=0&tqb3=15&tqb21=1&tqb7=1550&tqb8=1&tqb9=1&tqb10=1&tqb11=1&tqb12=1&tqb13=1&tqb14=1&tqb23=1&tqb24=1&tqb20=1&tqb22=1&tqb16=7&tqb18=&tqb19=&ra=2000"
        asyncio.run(self.load_data())
        print("Initial data loaded")
        
    async def load_data(self):
        """Loads new data in dataframe"""

        # Send a GET request to the URL
        response = httpx.get(self.url)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding="WINDOWS-1250")
            table = soup.find('table')
            # Read the table into a pandas DataFrame
            self.db = pd.read_html(str(table), header=0)[0]

            self.db['Url'] = self.db['Číslo'].apply(lambda x: f"https://www.psp.cz/sqw/historie.sqw?o=9&T={x.split('/')[0]}")

            # Save timestamp
            self.timestamp = datetime.now()


    async def query_data(self, query) -> str:
        """Searches the dataframe and returns information on the corresponding row as string"""

        query = str(query)
        if self.check_time_difference():
            await self.load_data()

        if not "/" in query:
            query += "/0"

        # Find the row(s) where 'Číslo' matches the provided value
        matched_rows = self.db[self.db['Číslo'] == query]

        if not matched_rows.empty:
            # Since 'Číslo' should be unique, we can take the first matched row
            row = matched_rows.iloc[0]
            # Format the row data into a string with headers and values
            formatted_data = '\n'.join([f"{col}: {row[col]}" for col in self.db.columns])
            additional_data = await self.get_details(row)

            proposal_url = f"\nOdkaz na text návrhu: https://www.psp.cz/sqw/text/tiskt.sqw?O=9&CT={query.split('/')[0]}&CT1=0"

            return formatted_data + "\n" + additional_data + proposal_url
        else:
            return f"Žádný sněmovní tisk č. {query} nenalezen."

    @staticmethod
    async def get_details(row):
        """Gets details of the specified amendment"""
        detailed_text = ""

        # Perform a GET request to obtain the HTML content
        url = row["Url"]
        response = httpx.get(url)
        html_content = response.text

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser', from_encoding="WINDOWS-1250")

        # Find the div with id="main-content"
        main_content_div = soup.find('div', id='main-content')
        section_divs = main_content_div.find_all('div', recursive=False, attrs={"class":"section"})
        okx_para = main_content_div.find('p', recursive=False, attrs={"class":"status okx"})

        for div in section_divs:
            detailed_text += div.get_text(separator=' ', strip=True)
            detailed_text += "\n"

        if okx_para:
            detailed_text += okx_para.get_text(separator=' ', strip=True)

        return detailed_text

    async def query_proposals(self, query):
        """Finds amendments based on act name"""
        if self.check_time_difference():
            await self.load_data()

        results: list = []
        for index, row in self.db.iterrows():
            if query in row["Krátký název"]:
                results.append(self.db.iloc[index].to_dict())

        result_text: str = ""
        for item in results:
            for key, value in item.items():
                result_text += f"{key}: {value}\n"
            result_text += "-------\n"

        if result_text != "":
            return result_text
        else:
            return "No such amendment found in Chamber of Deputies"

    def check_time_difference(self):

        current_time = datetime.now()
        time_difference = abs(self.timestamp - current_time)

        # Check if the difference is more than 12 hours
        if time_difference > timedelta(hours=12):
            return True
        else:
            return False

