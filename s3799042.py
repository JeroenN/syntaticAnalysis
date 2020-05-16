from __future__ import unicode_literals, print_function

import plac
import spacy
import requests

def main():
    nlp = spacy.load("en_core_web_sm")
    questions = create_questions()
    for question in questions:
        print(question)
        question = nlp(question)
        #print_dep(question)
        run_different_formulations(question)

def print_dep(question):
    for word in question:
        print(word.text + ": " + word.dep_)


def lemmafy(question):
    newQuestion = ""
    for word in question:
        newQuestion += word.lemma_
        newQuestion += " "
    return newQuestion

def debug(question):
    for word in question:
        if word.dep_ in ("nsubj"):
            print("nsubj(property):  " + word.text + "   " + "".join(w.text_with_ws for w in word.rights))
        if word.dep_ in ("pobj"):
            print("pobj:  " + word.text + "   entity:" + "".join(w.text_with_ws for w in word.subtree))


def get_property_word_nsubj(question):
    property = ""
    for word in question:
        if word.dep_ in "nsubj":
            for w in word.lefts:
                if not w.dep_ in ("det", "pobj", "prep"):
                    property += "".join(w.text_with_ws)
            property+=word.text
    return property

def get_entity_word_pobj(question):
    entity = ""
    for word in question:
        if word.dep_ in ("pobj"):
            for w in word.subtree:
                if not w.dep_ in ("det"):
                    entity += "".join(w.text_with_ws)
    return entity

def get_entity_word_nsubj(question):
    entity = ""
    for word in question:
        if word.dep_ in ("nsubj"):
            for w in word.subtree:
                if not w.dep_ in ("det"):
                    entity += "".join(w.text_with_ws)
    return entity

def get_entity_word_dobj(question):
    entity = ""
    for word in question:
        if word.dep_ in ("dobj"):
            for w in word.subtree:
                if not w.dep_ in ("det"):
                    entity += "".join(w.text_with_ws)
    return entity

def get_property_word_attr(question):
    property = ""
    for word in question:
        if word.dep_ in ("attr") and not word.tag_ in "WP":
            property+=word.text
    return property

def get_property_word_root(question):
    property = ""
    for word in question:
        if word.dep_ in ("ROOT"):
            property+=word.text
    return property

def get_entity_word_compound(question):
    entity = ""
    for word in question:
        if word.dep_ in ("ROOT"):
            for w in word.lefts:
                for a in w.subtree:
                    if not a.dep_ in ("det", "aux", "dobj"):
                        entity += "".join(a.text_with_ws)
    return entity

def get_entity_word_poss(question):
    entity = ""
    for word in question:
        if word.dep_ in ("poss"):
            for w in word.lefts:
                if not w.dep_ in ("det"):
                    entity += "".join(w.text_with_ws)
            entity += word.text
    return entity

def get_entity_codes(entity):
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action': 'wbsearchentities', 'language': 'en', 'format': 'json'}
    arrEntityCodes = []
    params['search'] = entity
    json = requests.get(url, params).json()
    for result in json['search']:
        arrEntityCodes.append(result['id'])

    if not arrEntityCodes:
        print("Entity error: no '" + entity + "' found")
        print("The program could not find an answer to this question. \n")
    return arrEntityCodes

#What is the taxon name of a wolf
def zero(question):
    propertyWord = get_property_word_nsubj(question)
    entityWord = get_entity_word_pobj(question)
    if propertyWord and entityWord and propertyWord !="Who":
        return run_question(propertyWord, entityWord)

#Who are the childeren of Albert Einstein
def one(question):
    propertyWord = get_property_word_attr(question)
    entityWord = get_entity_word_pobj(question)
    if propertyWord and entityWord:
        return run_question(propertyWord, entityWord)

#Who has invented the world wide web
def two(question):
    propertyWord = get_property_word_root(question)
    entityWord = get_entity_word_dobj(question)
    if propertyWord and entityWord:
        return run_question(propertyWord, entityWord)

#Who did invent the world wide web
def three(question):
    propertyWord = get_property_word_root(question)
    entityWord = get_entity_word_compound(question)
    if propertyWord and entityWord:
        return run_question(propertyWord, entityWord)

#Who was nikola Tesla's employer
def four(question):
    propertyWord = get_property_word_attr(question)
    entityWord = get_entity_word_poss(question)
    if propertyWord and entityWord:
        return run_question(propertyWord, entityWord)

def run_different_formulations(question):
    switcher = {
        0: zero(question),
        1: one(question),
        2: two(question),
        3: three(question),
        4: four(question)
    }
    for i in range(len(switcher)):
        answer = switcher.get(i, "not an formulation type")
        if answer:
            print(i)
            print(answer)
            #i = len(switcher)

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
    data = requests.get(url, headers=headers, params={'query': query, 'format': 'json'}).json()
    final_results = []
    for item in data['results']['bindings']:
        final_results.append(item['answerLabel']['value'])
    return final_results

def print_answer(answer):
    print(answer)


def create_questions():
    questions = []
    #questions.append("What did Alexander Fleming invent?")
    questions.append("Who was Nikola Tesla's employer?")
    questions.append("Who did invent the world wide web")
    questions.append("Who has invented the world wide web")
    questions.append("Who invented penicillin?")
    questions.append("Who are the children of Albert Einstein?")
    questions.append("What are the symptoms of the common cold?")
    questions.append("What is the atomic number of silver?")
    questions.append("What is the anti particle of an electron?")
    questions.append("What is the taxon name of a wolf?")
    questions.append("What did Alexander Fleming invent?")
    return questions

def run_question(propertyWord, entityWord):
    arrPropertycodes = get_property_codes(propertyWord)
    arrEntitycodes = get_entity_codes(entityWord)
    if arrEntitycodes and arrPropertycodes:
        entityCode = arrEntitycodes[0]
        propertyCode = arrPropertycodes[0]
        query = create_query(entityCode, propertyCode)
        return run_query(query)

if __name__ == "__main__":
    plac.call(main)
