# encoding: utf-8

    # TO DO:
    #
    # - Alterar estrutura para varrer todas as tags no source_code
    # - BeautifulSoup as tags no HTML, buscando o atual "a href" se configurado, ou "article", por exemplo
    # - Extrair descrição, texto e imagem segundo as configurações de tag

import mysql.connector
import time
import requests
import re
import json
from bs4 import BeautifulSoup


def strip_text(full_string, before, after):
    try:
        result = full_string.split(before, 1)[1]

        if (after is not None) & (len(str(after)) > 0):
            result = result.split(after, 1)[0]

        return result
    except:
        return None


def find_between(s, start, end, only_first, trim):
    try:
        result = re.findall("%s.+?%s" % (re.escape(start), re.escape(end)), s)

        if only_first:
            if trim:
                result = result[0]
                result = result[(len(start)):]
                result = result[:-(len(end))]
                return result
            else:
                return result[0]
        else:
            return result
    except:
        return None


def valid_article(url, description, source):
    try:
        source = source.rsplit('/', 1)[0]

        return \
            (url is not None) & \
            (description is not None) & \
            (url.find('#') == -1) & \
            (description.find('<') == -1) & \
            (url.startswith(source))

    except Exception as e:
        return False


def valid_string(string):
    return \
        (string != "") & \
        (string is not None)


def getSource(keyword, page_index):

    mydb = mysql.connector.connect(
        host="localhost",
        user="python",
        passwd="python",
        database='crawler'
    )

    # ativos = mydb.cursor(dictionary=True)
    #
    # ativos.execute("SELECT * FROM sources WHERE active = 1")
    #
    # ativos = ativos.fetchall()

    query_insert = mydb.cursor(dictionary=True)
    # query_tags = mydb.cursor(dictionary=True)

    try:

        print('Fetching Zoom for %s [page %d]...' % (keyword, page_index))

        page = requests.get('https://www.zoom.com.br/search?q=%s&page=%d' % (keyword, page_index))

        if page.status_code == 200:
            source_code = page.text

            search_end = (source_code.find('Não foram encontrados resultados com o termo buscado') != -1)

            print(search_end)

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
                        sql = "INSERT INTO zoom(category, description, img_url, price) VALUES (\"%s\", \"%s\", " \
                              "\"%s\", %.2f)" \
                            % (category, description, img_url, price)
                        query_insert.execute(sql)
                        mydb.commit()

                        print("====")
                        print('[%s] %s' % (category, description))
                        print('Price: %.2f' % price)

                    except Exception as e:
                        # print('Error recording: %s' % e)
                        continue

                    print("====")

                except Exception as e:
                    continue

            if not search_end:
                time.sleep(1)
                getSource(keyword, page_index + 1)

    except Exception as e:
        print(e)


print("Starting Zoom crawler..")
getSource('celular', 1)
getSource('livro', 1)
getSource('jogo', 1)
getSource('decoração', 1)
getSource('caneca', 1)
getSource('quadro', 1)
getSource('almofada', 1)
getSource('creme', 1)
getSource('camisetas', 1)
getSource('toalhas', 1)
getSource('perfumes', 1)
print("Done fetching!")