from langchain_community.tools.tavily_search import TavilySearchResults
from datetime import datetime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

model = ChatOpenAI(model="gpt-4")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

location = "Colchester, UK"
today = datetime.today().strftime('%A, %B %d, %Y')
print(f"Today is {today}")

search = TavilySearchResults(max_results=6)
search_results = search.invoke(f"What local events are not to be missed next week in {location}? The date is {today}.")
print(search_results)

# Now send the results to OpenAI for further processing
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Summarise the most up-to-date and applicable information from these search results."},
        {"role": "user", "content": str(search_results)}  # Convert search_results to a string
    ],
    max_tokens=600,
    n=1,
    temperature=0.7,
)
print(response.choices[0].message.content)