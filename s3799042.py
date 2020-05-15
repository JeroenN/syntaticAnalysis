from __future__ import unicode_literals, print_function

import plac
import spacy
import requests
from nltk import Tree

def main():
    questions = create_questions()
    run_questions(questions)


def debug(question):
    for word in question:
        if word.dep_ in ("nsubj"):
            print("nsubj(property):  " + word.text + "   " + "".join(w.text_with_ws for w in word.rights))
        if word.dep_ in ("pobj"):
            print("pobj:  " + word.text + "   entity:" + "".join(w.text_with_ws for w in word.subtree))


def get_property_word(question):
    property=""
    #for i in range(len(question)):
    for word in question:
        if word.dep_ in ("nsubj"):
            property = word.text
            print("property: " + property)
            return property
    if not property:
        print("no property was found")

def get_entity_word(question):
    entity=""
    b=[]
    for word in question:

        if word.dep_ in ("pobj"):
            for a in word.subtree:
                if not a.dep_ in ("det"):
                    b.append = a
            entity = "".join(w.text_with_ws for w in b)
            print("entity: " + entity)
            return entity
    if not entity:
        print("no entity was found")

def get_entity_codes(entity):
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action': 'wbsearchentities', 'language': 'en', 'format': 'json'}
    arrEntityCodes = []
    params['search'] = entity
    json = requests.get(url, params).json()
    for result in json['search']:
        arrEntityCodes.append(result['id'])

    if not arrEntityCodes:
        print("Entity error: no '" + entity +"' found")
        print("The program could not find an answer to this question. \n")
    return arrEntityCodes

def get_property_codes(property):
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action': 'wbsearchentities', 'language': 'en', 'format': 'json', 'type': 'property'}
    arrPropertycodes = []

    params['search'] = property
    json = requests.get(url, params).json()
    for result in json['search']:
        arrPropertycodes.append(result['id'])

    return arrPropertycodes

def create_query(entity, property):
    query = '''
        SELECT ?answer ?answerLabel WHERE{
            wd:''' + entity + ''' wdt:''' + property + ''' ?answer .
            SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en" .
        }
    }'''
    return query

def run_query(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (x11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/527.36'
    }
    url = 'https://query.wikidata.org/sparql'
    data = requests.get(url, headers= headers, params={'query': query, 'format': 'json'}).json()
    final_results = []
    for item in data['results']['bindings']:
        final_results.append(item['answerLabel']['value'])
    return final_results

def print_answer(answer):
    print(answer)

def create_questions():
    questions = []
    questions.append("Who are the crew members of the Apollo 11?")
    questions.append("Who is the inventor of the automobile?")
    questions.append("What are the parts of the lungs?")
    questions.append("What are the symptoms of the common cold?")
    questions.append("What is the atomic number of silver?")
    questions.append("What is the boiling point of alcohol?")
    questions.append("What is the birth date of Maria Skłodowska?")
    questions.append("What is the anti particle of an electron?")
    questions.append("What is the taxon name of a wolf?")
    questions.append("Who are the children of Albert Einstein?")
    return questions

def tok_format(tok):
    return "-".join([tok.orth_, tok.tag_, tok.dep_])


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
    else:
        return tok_format(node)

def run_questions(questions):
    nlp = spacy.load("en_core_web_sm")
    for i in range(len(questions)):
        line = questions[i]
        print(line)
        line = nlp(line)
        #[to_nltk_tree(sent.root).pretty_print() for sent in line.sents]

        propertyWord = get_property_word(line)
        entityWord = get_entity_word(line)
        if(entityWord == "the lungs"):
            entityWord = "lungs"
        if propertyWord and entityWord:
            arrPropertycodes = get_property_codes(propertyWord)
            arrEntitycodes = get_entity_codes(entityWord)
            if arrEntitycodes and arrPropertycodes:
                    entityCode =arrEntitycodes[0]
                    propertyCode = arrPropertycodes[0]
                    query = create_query(entityCode, propertyCode)
                    answer = run_query(query)
                    if answer:
                        print_answer(answer)
                    else:
                        print("Could not find an answer \n")


if __name__ == "__main__":
    plac.call(main)