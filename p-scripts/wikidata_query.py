from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

import pprint
import time

pp = pprint.PrettyPrinter(indent=4)

authlist = {}
# pp.pprint(res['results']['bindings'])
#pp.pprint(res['results']['bindings'][0]['human']['value'].rsplit('/', 1)[-1])


def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


def get_qnumber_sparql(wikisearch, birthdate_begin, birthdate_end):

    human = wikisearch.split()
    if len(human) == 1:
        return ""
    if authlist.get(wikisearch):
        if len(authlist[wikisearch]['results']['bindings']) > 0:
            return authlist[wikisearch]['results']['bindings'][0]['human']['value'].rsplit('/', 1)[-1]
        else:
            return ""
    humanname = safe_list_get(human, 1, "")
    humanfamily = safe_list_get(human, 0, "")
    humanpatronym = safe_list_get(human, 2, "")

    sparql_query = """
    SELECT DISTINCT ?human ?humanLabel ?dateOfBirth ?giveNameLabel ?familyNameLabel ?patronymLabel WHERE {
    ?human wdt:P31 wd:Q5 .
    ?human wdt:P106 wd:Q36180 .
    ?human wdt:P734 ?familyName .
    ?human wdt:P735 ?giveName.
    ?familyName ?label "%(humanfamily)s"@ru .
    ?giveName ?label "%(humanname)s"@ru .
    OPTIONAL { ?human wdt:P2976 ?patronym . 
              ?patronym ?label "%(humanpatronym)s"@ru .
    }
    OPTIONAL { ?human wdt:P569 ?dateOfBirth. }
    hint:Prior hint:rangeSafe "true"^^xsd:boolean.
    FILTER(("%(birthdate_begin)s-00-00"^^xsd:dateTime <= ?dateOfBirth) && (?dateOfBirth < "%(birthdate_end)s-12-31"^^xsd:dateTime))
    SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
    }
    """ % {'humanfamily': humanfamily, 'humanname': humanname, 'humanpatronym': humanpatronym, 'birthdate_begin': birthdate_begin, 'birthdate_end': birthdate_end}
    res = {}
    counter = 0
    while not res:
        if counter > 0:
            time.sleep(1)
        if counter > 10:
            return ""
        try:
            counter = counter+1
            res = return_sparql_query_results(sparql_query)
        except ValueError:
            print("Error %(wikisearch)s retrying" % {'wikisearch': wikisearch})

    if len(res['results']['bindings']) == 0:
        sparql_query = """
      SELECT DISTINCT ?human ?humanLabel ?dateOfBirth ?giveNameLabel ?familyNameLabel ?patronymLabel WHERE {
      ?human wdt:P31 wd:Q5 .
      ?human wdt:P734 ?familyName .
      ?human wdt:P735 ?giveName.
      ?familyName ?label "%(humanfamily)s"@ru .
      ?giveName ?label "%(humanname)s"@ru .
      OPTIONAL { ?human wdt:P2976 ?patronym . 
                ?patronym ?label "%(humanpatronym)s"@ru .
      }
      OPTIONAL { ?human wdt:P569 ?dateOfBirth. }
      hint:Prior hint:rangeSafe "true"^^xsd:boolean.
      FILTER(("%(birthdate_begin)s-00-00"^^xsd:dateTime <= ?dateOfBirth) && (?dateOfBirth < "%(birthdate_end)s-12-31"^^xsd:dateTime))
      SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
      }
      """ % {'humanfamily': humanfamily, 'humanname': humanname, 'humanpatronym': humanpatronym, 'birthdate_begin': birthdate_begin, 'birthdate_end': birthdate_end}
        res = {}
        counter = 0
        while not res:
            if counter > 0:
                time.sleep(1)
            if counter > 10:
                return ""
            try:
                counter = counter+1
                res = return_sparql_query_results(sparql_query)
            except ValueError:
                print("Error %(wikisearch)s retrying" %
                      {'wikisearch': wikisearch})

    authlist[wikisearch] = res
    # logging.info(str(res))
    if len(res['results']['bindings']) > 0:
        return res['results']['bindings'][0]['human']['value'].rsplit('/', 1)[-1]
    return ""

# res = get_qnumber_sparql("Маркс Карл Генрих","1800","1899")
# print(res)
