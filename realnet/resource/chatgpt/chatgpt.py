import os
import random
import string
import requests
from dotenv import *
from flask import Flask, request, jsonify

from realnet.resource.items.items import Items
from realnet.core.type import Item, Instance

path = os.path.join(os.getcwd(), ".env")
if os.path.exists(path):
    load_dotenv(dotenv_path=path)

import re

class Chatgpt(Items):

    def call_chatgpt_api(self, prompt):
        CHATGPT_API_KEY = os.getenv('REALNET_CHATGPT_API_KEY', 'your_api_key_here')
        CHATGPT_API_URL = os.getenv('REALNET_CHATGPT_API_URL', 'https://api.openai.com/v1/engines/davinci-codex/completions')
        headers = {
            "Authorization": f"Bearer {CHATGPT_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ] # You can adjust this value as needed
        }
        response = requests.post(CHATGPT_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def get_taxonomic_info(self, word):
        taxonomy_prompt = f"give me a ### delimited 4-tuple response where tuple elements correspond to the following specs in this order: t1. path last end of th corresponding Wikipedia url of the term {word} t2. the Wikipedia link corresponding to the term {word}, t3. list 50 most important attributes described in the wikipedia page text corresponding to term {word} in ('name': 'value') pairs embedded in [], t4. list of any relevant internet links for term {word} based on its Wikipedia page embedded as []. Write the tuple in the format t1###t2###t3###t4)"
        taxonomy_and_link_and_attributes_and_links = self.call_chatgpt_api(taxonomy_prompt)
        answers = taxonomy_and_link_and_attributes_and_links.strip().split('###')
        attributes = '[]'
        links = '[]'
        if len(answers) != 4:
            print(answers)
            taxonomy, wikimedia_link, attributes, links = '', '', '[]', '[]'
        else:
            taxonomy, wikimedia_link, attributes, links = answers

        # Process attributes and links
        attribute_list = []

        for string in attributes.strip('[]').split(','):  # remove the square brackets and split the string by comma
            string = string.strip("' (){}")  # remove any leading/trailing single quotes and whitespace
            if ':' in string:
                name, value = string.split(':', 1)
                attribute_list.append({"name": name.strip("' "), "value": value.strip("' ")})
        
        link_list = []
        for string in links.strip('[]').split(','):
            link = string.strip("' ")  # remove any leading/trailing single quotes and whitespace
            link_list.append(link)

        return taxonomy, wikimedia_link, attribute_list, link_list

    def starts_with_number_dot(self, word):
        pattern = r'^\d+\.' # regular expression pattern to match number followed by dot at the start of the word
        return bool(re.match(pattern, word))
    
    def in_whitelist(self, word):
        return not self.starts_with_number_dot(word) and all(char.isalnum() or char == '.' for char in word)

    def parse_response(self, module, response_text):
        words = response_text.split()
        objects = []
        for word in words:
            if self.in_whitelist(word):
                taxonomy, wikimedia_link, attributes, links = self.get_taxonomic_info(word)

                # Add wikimedia_link to attributes
                attributes.append({"name": "wikimedia_link", "value": wikimedia_link})
                attributes.append({"name": "links", "value": links})

                param_attributes = dict()
                for attribute in attributes:
                    param_attributes[attribute['name']] = attribute['value']

                param_attributes['resource'] = 'chatgpt'
                param_attributes['icon'] = 'square'

                physical_object = {
                    "name": word,
                    "type": taxonomy,
                    "attributes": param_attributes,
                }
                objects.append(self.get_or_create_item(module, physical_object))
        return objects
    
    def get_or_create_item(self, module, item):
        # Check if item already exists
        existing_item = module.find_items({'name': item['name']})
        if existing_item:
            return existing_item[0]
        else:
            # Create new item
            item_type = module.get_type_by_name(item['type'])
            if not item_type:
                item_type = module.create_type(name=item['type'], base='Type', attributes=item['attributes'])

            random_string = '' #''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
            item_instance = module.create_instance(name=item['name'] + random_string, type=item_type.name)
            item = module.create_item(name=item['name'] + random_string, type=item_type.name, instance_id=item_instance.id)
            return item
    
    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        input_message = args.get("name",[])
        if not input_message:
            return []

        chatgpt_response = self.call_chatgpt_api(input_message[0])
        items = self.parse_response(module, chatgpt_response)
        return items
        
        