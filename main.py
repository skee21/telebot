import os
import telebot
from keep_alive import keep_alive
from bs4 import BeautifulSoup
import requests
import csv

url = "https://libgen.is/search.php"
r = requests.get(url)

#with open('n1.html', 'wb') as file:
  #file.write(r.content)

my_secret = os.environ['KEY']
bot = telebot.TeleBot(my_secret)

def search_libgen(keyword):
  url = f'http://libgen.is/search.php?req={keyword}&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def'
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')
  results = soup.find_all('table', class_='c')

  books = []

  for result in results:
    title_tag = result.find('a', href=True)
    if title_tag:
      title = title_tag.text.strip()
      url = 'https://libgen.is' + title_tag['href']
      books.append({'title': title, 'url': url})

  return books

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
  user = message.from_user
  bot.reply_to(message, f"Hello {user.first_name}")

@bot.message_handler(commands=['search'])
def handle_search(message):
  keyword = message.text.split('/search ', 1)[1]
  search_results = search_libgen(keyword)
  
  with open('search_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['title', 'url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for result in search_results:
      writer.writerow(result)

  with open('search_results.csv', 'rb') as csvfile:
    bot.send_document(message.chat.id, csvfile)
  
keep_alive()
bot.infinity_polling()