# encoding: utf-8

# TO DO:
#
# - Alterar estrutura para varrer todas as tags no source_code
# - BeautifulSoup as tags no HTML, buscando o atual "a href" se configurado, ou "article", por exemplo
# - Extrair descrição, texto e imagem segundo as configurações de tag

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from json import JSONEncoder

global products


class Product:
    def __init__(self, category, description, img_url, price):
        self.category = category
        self.description = description
        self.img_url = img_url
        self.price = price


class ProductEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def getSource(keyword, page_index):
    try:
        if page_index == 1:
            products = json.loads('{"data":[]}')

        print_log('Fetching Zoom for %s [page %d]...' % (keyword, page_index))

        page = requests.get('https://www.zoom.com.br/search?q=%s&page=%d' % (keyword, page_index))

        if page.status_code == 200:
            source_code = page.text

            search_end = (source_code.find('Não foram encontrados resultados com o termo buscado') != -1)

            print_log(search_end)

            soup_page = BeautifulSoup(source_code, "lxml")

            json_data = json.loads(soup_page.find(id='__NEXT_DATA__').contents[0])
            json_data = json_data["props"]
            json_data = json_data["pageProps"]
            json_data = json_data["resultsState"]
            json_data = json_data["rawResults"][0]

            # added_items = 0

            for item in json_data["hits"]:
                try:
                    category = item["categorySeoUrl"]
                    description = item["name"]
                    img_url = item["image"]
                    price = item["price"]

                    try:
                        search_product = Product(category, description, img_url, price)

                        products['data'].append(search_product)
                        # json_data[len(json_data)]['category'] = category
                        # json_data[len(json_data)]['description'] = description
                        # json_data[len(json_data)]['img_url'] = img_url
                        # json_data[len(json_data)]['price'] = price

                        print_log("====")
                        print_log('[%s] %s' % (category, description))
                        print_log('Price: %.2f' % price)

                    except Exception as e:
                        # print_log('Error recording: %s' % e)
                        continue

                    print_log("====")

                except Exception as e:
                    continue

            # if (not search_end) or (page_index > 5):
            #     time.sleep(1)
            #     getSource(keyword, page_index + 1)

        result_data = ProductEncoder().encode(products)
        return result_data

    except Exception as e:
        print_log(e)
        products = json.loads('{"data":[]}')


def print_log(message):
    with open('messages.log', 'a') as logfile:
        logfile.write('[%s] %s \n' % (datetime.now().strftime('%d/%m/%Y %X'), str(message)))
