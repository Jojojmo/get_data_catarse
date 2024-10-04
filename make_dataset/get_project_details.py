import json
import httpx
import os
import pandas as pd
import numpy as np
import logging
from rich.logging import RichHandler
from httpx import AsyncClient, RequestError
import time
import asyncio

# Configuração do logger
def setup_logging():
    # Crie um manipulador de arquivos para o log
    file_handler = logging.FileHandler('logs.txt')
    file_handler.setLevel(logging.INFO)  # Ajuste o nível de logging conforme necessário

    # Crie um manipulador RichHandler para a saída
    rich_handler = RichHandler(rich_tracebacks=True)
    rich_handler.setLevel(logging.INFO)  # Ajuste o nível de logging conforme necessário

    # Configure o logger
    logging.basicConfig(
        level=logging.INFO,  # Ajuste o nível de logging conforme necessário
        format="%(message)s",
        handlers=[file_handler, rich_handler]
    )

# Configure o logging
setup_logging()


#####

selected_attributes = ['project_id', 'id', 'name', 'budget', 'goal', 
                       'about_html', 'category_id', 'progress', 'pledged', 
                       'total_contributions', 'total_contributors', 'state', 
                       'mode', 'state_order', 'expires_at', 'online_date', 
                       'online_days', 'posts_count', 'total_posts', 
                       'contributed_by_friends', 'tag_list',  
                       'is_adult_content', 'content_rating', 'recommended']

boolean_attributes = ["video_embed_url", "video_url", "thumb_image"]

##### 

class Create_record:
    def __init__(self, content):
        self.content = content
        self.registry = {}
        self.make_selected_attributes()
        self.make_boolean_attributes()
        self.make_address()

    def make_selected_attributes(self):
        for attribute in selected_attributes:
            self.registry[attribute] = self.content.get(attribute)


    def make_boolean_attributes(self):
        for attribute in boolean_attributes:
            if self.content.get(attribute):
                self.registry[attribute] = True
            else:
                self.registry[attribute] = False


    def make_address(self):
        self.registry['city'] = None
        self.registry['state_acronym'] = None
        if self.content.get('address'):
            del self.content["address"]["state"]
            for key, value in self.content['address'].items():
                self.registry[key] = value



def make_index():
    projects_finished = httpx.get("https://api.catarse.me/finished_projects?order=state_order.asc%2Cstate.desc%2Cpledged.desc")

    if projects_finished.status_code == 200:
        content_json_finished = json.loads(projects_finished.content)
        index = list()
        for obj in content_json_finished:
            if obj.get('project_id') and obj.get("mode") != 'sub':
                index.append(obj.get('project_id'))
    series_index = pd.Series(index)
    series_index.to_pickle('index_project_details.pkl')


def load_index():
    try:
        return pd.read_pickle('index_project_details.pkl')
    except:
        make_index()
        return pd.read_pickle('index_project_details.pkl')


async def api_request(index, data_api):
    url = f"https://api.catarse.me/project_details?project_id=eq.{index}"
    try:
        async with AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            make_registry(response.json(), data_api)

    except RequestError as e:
        data_api.append(None)


def make_registry(response_json, data_api):
    try:
        result = Create_record(response_json[0]).registry
        data_api.append(result)
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error occurred: {json_err}") 
        data_api.append(None)



async def process_data(indices, data_api, per_minute=200):
    times = indices.shape[0] // per_minute
    sliced = np.array_split( indices,int(times))
    all_tasks = list()
    for chunck in sliced:
        for index in chunck:
            all_tasks.append(api_request(index, data_api))


    while all_tasks:
        # A variavel per_minute indica o Número de processos por task
        batch = all_tasks[:per_minute]
        all_tasks = all_tasks[per_minute:]

        start_time = time.time()

        await asyncio.gather(*batch)

        elapsed_time = time.time() - start_time
        remaining_time = max(0, 60 - elapsed_time)

        if remaining_time > 0:
            await asyncio.sleep(remaining_time)


#Colocar uma função para que em X interações fosse feito o dump parcial
#para poder continuar em outro momento ou recomeçar de um ponto após algum erro

if __name__ == '__main__':
    index_finished = load_index()
    data_api = list()
    asyncio.run(process_data(index_finished, data_api, 300))
    with open('project_details.json', 'w', encoding='utf-8') as f:
        # Grava os dados no arquivo em formato JSON
        json.dump(data_api, f, indent=4, ensure_ascii=False)