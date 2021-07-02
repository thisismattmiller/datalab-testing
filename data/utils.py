from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import URIRef, Graph, Literal, plugin, Namespace
from rdflib.serializer import Serializer
from django.conf import settings
import operator
import sys
import os

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def return_objects(uri):
	sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
	sparql.setCredentials(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD'])
	sparql.setQuery("""
	    SELECT *
	    WHERE { %s ?p ?o }
	    LIMIT 9000
	""" % (uri))
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	return results
	# for result in results["results"]["bindings"]:
	#     print(result)

def return_subjects(uri):
	sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
	sparql.setCredentials(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD'])
	sparql.setQuery("""
	    SELECT *
	    WHERE { ?s ?p %s }
	    LIMIT 9000
	""" % (uri))
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	return results
	# for result in results["results"]["bindings"]:
	#     print(result)
"""
Returns the label and date of uris given good for events
"""
def return_label_date(uris):

	uri_chunks = chunks(uris,100)

	all_results = {'head': {'vars': ['uri', 'o', 'p']}, 'results': {'bindings': [] } }

	for chunk in uri_chunks:
		sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
		sparql.setCredentials(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD'])

		query = 'PREFIX dcterms: <http://purl.org/dc/terms/>'
		query = query + 'SELECT * WHERE{'
		query = query + '{?uri rdfs:label ?o . ?uri ?p ?o .}'
		query = query + 'UNION'
		query = query + '{?uri dcterms:date ?o . ?uri ?p ?o .}'
		query = query + 'FILTER (?uri IN ('+ ','.join(chunk)  +'))'
		query = query + '}'

		sparql.setQuery(query)
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			all_results['results']['bindings'].append(result)


	return all_results


"""
Returns the names of the URIs given, either as foaf name or label depending on how they were stored
"""
def return_name(uris):

	uri_chunks = chunks(uris,100)

	all_results = {'head': {'vars': ['uri', 'o', 'p']}, 'results': {'bindings': [] } }
	for chunk in uri_chunks:


		sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
		sparql.setCredentials(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD'])
		query = 'PREFIX foaf: <http://xmlns.com/foaf/0.1/>'
		query = query + 'SELECT * WHERE{'
		query = query + '{?uri rdfs:label ?o . ?uri ?p ?o .}'
		query = query + 'UNION'
		query = query + '{?uri foaf:name ?o . ?uri ?p ?o .}'
		query = query + 'FILTER (?uri IN ('+ ','.join(chunk)  +'))'
		query = query + '}'

		sparql.setQuery(query)
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			all_results['results']['bindings'].append(result)


	return all_results

"""
Returns the work URIs for a work event id
"""
def return_works_from_event(uris):

	sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
	sparql.setCredentials(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD'])

	query = 'PREFIX dcterms: <http://purl.org/dc/terms/>'
	query = query + 'SELECT * WHERE{'
	query = query + '?uri <http://purl.org/NET/c4dm/event.owl#product> ?o . ?uri ?p ?o .'
	query = query + 'FILTER (?uri IN ('+ ','.join(uris)  +'))'
	query = query + '}'


	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	event_work_map = {}
	work_uris = []

	for result in results["results"]["bindings"]:
		work_uris.append('<' + result['o']['value'] + '>')
		event_work_map[result['uri']['value']] = result['o']['value']

	labels = return_label_date(work_uris)

	for label in labels["results"]["bindings"]:
		for key in event_work_map:
			if event_work_map[key] == label['uri']['value']:
				event_work_map[key] = label['o']['value']

	return event_work_map


"""
Returns the work URIs for a work event id
"""
def return_serialized_subjects(uri,type):
	sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
	sparql.setCredentials(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD'])

	if uri[0] != '<':
		uri_no_bracket = uri
		uri = '<' + uri + '>'
	else:
		uri_no_bracket = uri[1:]
		uri_no_bracket = uri_no_bracket[:-1]


	query = 'SELECT * WHERE{'
	query = query + uri + ' ?p ?o .'
	query = query + '}'

	sparql.setQuery(query)

	g = Graph()

	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	for result in results["results"]["bindings"]:
		if (result['o']['type'] == 'uri'):
			g.add( (URIRef(uri_no_bracket), URIRef(result['p']['value']) , URIRef(result['o']['value'])) )
		else:
			if 'datatype' in result['o']:
				g.add( (URIRef(uri_no_bracket), URIRef(result['p']['value']) , Literal(result['o']['value'], datatype=URIRef(result['o']['datatype']))) )
			else:
				g.add( (URIRef(uri_no_bracket), URIRef(result['p']['value']) , Literal(result['o']['value'])) )


	if len(g) == 0:
		return '404'

	if (type == 'xml'):
		return g.serialize(format="xml")
	elif (type == 'n3'):
		return g.serialize(format="n3")
	elif (type == 'nt'):
		return g.serialize(format="nt")
	elif (type == 'turtle'):
		return g.serialize(format="turtle")
	elif (type == 'jsonld'):
		return g.serialize(format="json-ld")
	else:
		return g.serialize(format="nt")



def format_events_dict(event_uri):


	o = return_objects(event_uri)
	s = return_subjects(event_uri)
	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])

	agents = []
	dates = []
	types = []
	labels = []
	unmapped = []
	product = []
	venue = []

	for result in o["results"]["bindings"]:
		if '/names/' in result['o']['value']:
			agents.append('<'+result['o']['value']+'>')

		if result['p']['value'] == 'http://purl.org/NET/c4dm/event.owl#product':
			product.append(result['o']['value'])
		elif result['p']['value'] == 'http://purl.org/dc/terms/date':
			dates.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		elif result['p']['value'] == 'http://purl.org/NET/c4dm/event.owl#place':
			venue.append('<'+result['o']['value']+'>')


		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			labels.append(result['o']['value'])
		elif '/names/' in result['o']['value']:
			pass
		else:
			unmapped.append([result['p']['value'], result['o']['value']])



	product.sort()
	people = []

	agents = return_name(agents)
	for agent in agents["results"]["bindings"]:

		#look for the triple in the main set
		for result in o["results"]["bindings"]:
			if result['o']['value'] == agent['uri']['value']:
				people.append([agent['uri']['value'], agent['o']['value'],result['p']['value'].replace('http://purl.org/ontology/mo/','mo:') ])

	venue = return_name(venue)
	venues = []
	for v in venue["results"]["bindings"]:
		venues.append([v['uri']['value'],v['o']['value']])

	product_uris = []
	for p in product:
		product_uris.append('<'+p+'>')

	event_work_map = return_works_from_event(product_uris)




	product_with_labels = []
	for p in product:

		if p in event_work_map:
			product_with_labels.append([p,event_work_map[p]])
		else:
			product_with_labels.append([p,"???"])

	event = {
		'dcterms_date' : dates,
		'rdf_type' : types,
		'rdfs_label' : labels,
		'rdfs_label_string' : (',').join(labels),
		'unmapped' : unmapped,
		'people' : people,
		'product': product_with_labels,
		'venues' : venues,
		'total_triples' : total_triples
	}




	return event


def format_product_dict(product_uri):

	o = return_objects(product_uri)
	s = return_subjects(product_uri)
	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])

	types = []
	unmapped = []
	events = []

	for result in o["results"]["bindings"]:
		if result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		else:
			unmapped.append([result['p']['value'], result['o']['value']])


	for result in s["results"]["bindings"]:
		if result['p']['value'] == 'http://purl.org/NET/c4dm/event.owl#product':
			events.append('<'+result['s']['value']+'>')



	work_labels = return_works_from_event([product_uri])
	for key in work_labels:
		work_labels = [[key,work_labels[key]]]


	events = return_label_date(events)

	events_map = {}

	for result in events["results"]["bindings"]:
		uri = result['uri']['value']
		if uri not in events_map:
			events_map[uri] = { 'rdfs:label' : '', 'dcterms:date' : '' }

		if result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			events_map[uri]['rdfs:label'] = result['o']['value']

		if result['p']['value'] == 'http://purl.org/dc/terms/date':
			events_map[uri]['dcterms:date'] = result['o']['value']

	events = []

	for key in events_map:
		events.append([key,events_map[key]['rdfs:label'],events_map[key]['dcterms:date']])


	product = {
		'rdf_type': types,
		'work_label' : work_labels[0][1],
		'events' : events,
		'total_triples' : total_triples
	}

	return product



def format_venues_dict(venue_uri):
	o = return_objects(venue_uri)
	s = return_subjects(venue_uri)
	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])

	types = []
	labels = []
	unmapped = []
	comment = []
	parent = []
	match = []
	historical_name = []
	contains_place = []

	for result in o["results"]["bindings"]:
		if result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#comment':
			comment.append(result['o']['value'])
		elif result['p']['value'] == 'http://purl.org/dc/terms/date':
			dates.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.geonames.org/ontology#parentFeature':
			parent.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			labels.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.geonames.org/ontology#historicalName':
			historical_name.append(result['o']['value'])
		elif result['p']['value'] == 'http://schema.org/containsPlace':
			contains_place.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2004/02/skos/core#exactMatch':
			match.append(result['o']['value'])
		else:
			unmapped.append([result['p']['value'], result['o']['value']])




	venue = {
		'rdf_type' : types,
		'rdfs_label' : labels,
		'unmapped' : unmapped,
		'parent' : parent,
		'comment': comment,
		'historical_name' : historical_name,
		'contains_place' : contains_place,
		'match' : match,
		'total_triples' : total_triples
	}




	return venue

def format_roles_dict(role_uri):
	o = return_objects(role_uri)
	s = return_subjects(role_uri)
	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])

	types = []
	labels = []
	unmapped = []
	comment = []

	for result in o["results"]["bindings"]:
		if result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#comment':
			comment.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			labels.append(result['o']['value'])
		else:
			unmapped.append([result['p']['value'], result['o']['value']])


	role = {
		'rdf_type' : types,
		'rdfs_label' : labels,
		'unmapped' : unmapped,
		'comment': comment,
		'total_triples' : total_triples
	}
	return role

def format_ensembles_dict(ensembles_uri):
	o = return_objects(ensembles_uri)
	s = return_subjects(ensembles_uri)

	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])


	types = []
	labels = []
	unmapped = []
	comment = []

	for result in o["results"]["bindings"]:
		if result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#comment':
			comment.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			labels.append(result['o']['value'])
		else:
			unmapped.append([result['p']['value'], result['o']['value']])


	role = {
		'rdf_type' : types,
		'rdfs_label' : labels,
		'unmapped' : unmapped,
		'comment': comment,
		'total_triples': total_triples,
		'total_triples' : total_triples
	}
	return role




def format_instruments_dict(instrument_uri):
	o = return_objects(instrument_uri)
	s = return_subjects(instrument_uri)
	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])

	types = []
	labels = []
	unmapped = []
	comment = []
	match = []

	for result in o["results"]["bindings"]:
		if result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#comment':
			comment.append(result['o']['value'])
		elif result['p']['value'] == 'http://purl.org/dc/terms/date':
			dates.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			labels.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2004/02/skos/core#exactMatch':
			match.append(result['o']['value'])
		else:
			unmapped.append([result['p']['value'], result['o']['value']])


	instrument = {
		'rdf_type' : types,
		'rdfs_label' : labels,
		'unmapped' : unmapped,
		'comment': comment,
		'match' : match,
		'total_triples' : total_triples
	}

	return instrument

def format_genres_dict(genre_uri):
	o = return_objects(genre_uri)
	s = return_subjects(genre_uri)
	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])

	types = []
	labels = []
	unmapped = []
	comment = []
	match = []

	for result in o["results"]["bindings"]:
		if result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#comment':
			comment.append(result['o']['value'])
		elif result['p']['value'] == 'http://purl.org/dc/terms/date':
			dates.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			labels.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2004/02/skos/core#exactMatch':
			match.append(result['o']['value'])
		else:
			unmapped.append([result['p']['value'], result['o']['value']])


	genre = {
		'rdf_type' : types,
		'rdfs_label' : labels,
		'unmapped' : unmapped,
		'comment': comment,
		'match' : match,
		'total_triples' : total_triples
	}

	return genre


def format_vocab_roles_dict(roles_uri):
	o = return_objects(roles_uri)
	s = return_subjects(roles_uri)
	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])

	types = []
	labels = []
	unmapped = []
	seealso = []
	domain = []
	isdefinedby = []


	for result in o["results"]["bindings"]:
		if result['p']['value'] == 'http://purl.org/dc/terms/date':
			dates.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			labels.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#seeAlso':
			seealso.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#domain':
			domain.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#isDefinedBy':
			isdefinedby.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#subPropertyOf':
			pass
		else:
			unmapped.append([result['p']['value'], result['o']['value']])


	role = {
		'rdf_type' : types,
		'rdfs_label' : labels,
		'unmapped' : unmapped,
		'seealso' : seealso,
		'domain' : domain,
		'isdefinedby' : isdefinedby,
		'total_triples' : total_triples
	}




	return role

def format_names_dict(name_uri):
	o = return_objects(name_uri)
	s = return_subjects(name_uri)

	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])

	types = []
	labels = []
	name = []
	unmapped = []
	comment = []
	parent = []
	match = []
	profession_or_occupation = []
	labels_map = []
	played_instrument = []
	birth = []
	death = []

	for result in o["results"]["bindings"]:
		if result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#comment':
			comment.append(result['o']['value'])
		elif result['p']['value'] == 'http://purl.org/dc/terms/date':
			dates.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.geonames.org/ontology#parentFeature':
			parent.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			labels.append(result['o']['value'])
		elif result['p']['value'] == 'http://xmlns.com/foaf/0.1/name':
			name.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.geonames.org/ontology#historicalName':
			historical_name.append(result['o']['value'])
		elif result['p']['value'] == 'http://schema.org/containsPlace':
			contains_place.append(result['o']['value'])
		elif result['p']['value'] == 'http://d-nb.info/standards/elementset/gnd#professionOrOccupation':
			labels_map.append('<'+result['o']['value']+'>')
			profession_or_occupation.append(result['o']['value'])
		elif result['p']['value'] == 'http://d-nb.info/standards/elementset/gnd#playedInstrument':
			played_instrument.append(result['o']['value'])
			labels_map.append('<'+result['o']['value']+'>')

		elif result['p']['value'] == 'http://xmlns.com/foaf/0.1/name':
			name.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2004/02/skos/core#exactMatch':
			match.append(result['o']['value'])

		elif result['p']['value'] == 'http://schema.org/birthDate':
			birth.append(result['o']['value'])
		elif result['p']['value'] == 'http://schema.org/deathDate':
			death.append(result['o']['value'])
		else:
			result['p']['value'] = result['p']['value'].replace('http://schema.org/','schema:')
			result['p']['value'] = result['p']['value'].replace('http://dbpedia.org/ontology/','dbo:')



			unmapped.append([result['p']['value'], result['o']['value']])


	labels_map = return_name(labels_map)

	played_instrument_with_labels = []
	profession_or_occupation_with_labels = []
	for p in played_instrument:
		for result in labels_map["results"]["bindings"]:
			if result['uri']['value'] in p:
				played_instrument_with_labels.append([p,result['o']['value']])

	for p in profession_or_occupation:
		for result in labels_map["results"]["bindings"]:
			if result['uri']['value'] in p:
				profession_or_occupation_with_labels.append([p,result['o']['value']])



	display_name = ''


	if len(name) > 0:
		display_name = name[0]

	if len(labels) > 0:
		display_name = labels[0]
	name = {
		'rdf_type' : types,
		'rdfs_label' : labels,
		'display_name': display_name,
		'name' : name,
		'unmapped' : unmapped,
		'parent' : parent,
		'comment': comment,
		'match' : match,
		'birth' : birth,
		'death' : death,
		'profession_or_occupation': profession_or_occupation_with_labels,
		'played_instrument': played_instrument_with_labels,
		'total_triples' : total_triples
	}




	return name
def format_works_dict(work_uri):


	o = return_objects(work_uri)
	s = return_subjects(work_uri)
	total_triples = len(o["results"]["bindings"]) + len(s["results"]["bindings"])

	#these will be all the event works, so we just want to get the parent events
	events = []
	for result in s["results"]["bindings"]:
		if 'http://data.carnegiehall.org/events/' in result['s']['value']:

			uri = result['s']['value'].split('/work_')[0]

			if uri not in events:
				events.append('<' + uri + '>')

	#events
	events = return_label_date(events)
	events_map = {}

	for result in events["results"]["bindings"]:
		uri = result['uri']['value']
		if uri not in events_map:
			events_map[uri] = { 'rdfs:label' : '', 'dcterms:date' : '' }

		if result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			events_map[uri]['rdfs:label'] = result['o']['value']

		if result['p']['value'] == 'http://purl.org/dc/terms/date':
			events_map[uri]['dcterms:date'] = result['o']['value']



	creators = []
	creators_map = []
	dates = []
	types = []
	labels = []
	unmapped = []
	match = []

	for result in o["results"]["bindings"]:
		if result['p']['value'] == 'http://purl.org/dc/terms/creator':
			creators.append('<' + result['o']['value'] + '>')
		elif result['p']['value'] == 'http://purl.org/dc/terms/created':
			dates.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			types.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
			labels.append(result['o']['value'])
		elif result['p']['value'] == 'http://www.w3.org/2004/02/skos/core#exactMatch':
			match.append(result['o']['value'])
		else:
			unmapped.append([result['p']['value'], result['o']['value']])


	creators = return_name(creators)
	for result in creators["results"]["bindings"]:
		uri = result['uri']['value']
		creators_map.append([uri,result['o']['value']])


	events = []
	for key, value in events_map.items():
		events.append([key,value['rdfs:label'],value['dcterms:date']])

	events.sort(key=lambda x: x[2], reverse=True)

	work = {
		'dcterms_creator' : creators_map,
		'dcterms_created' : dates,
		'rdf_type' : types,
		'rdfs_label' : labels,
		'rdfs_label_string' : (',').join(labels),
		'events' : events,
		'unmapped' : unmapped,
		'skos_exact_match' : match,
		'total_triples' : total_triples
	}

	return work



def format_vocabulary_role_dict():

	data = return_serialized_vocabulary_role('data')
	data_dict = {}
	onto_dict = {}
	for x in data['roles']:
		if 's' in x:
			if x['s']['value'] not in data_dict:
				data_dict[x['s']['value']] = {'label':None,'seealso':None}

		if 'p' in x:
			if x['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#label':
				data_dict[x['s']['value']]['label'] = x['oo']['value']
			elif x['p']['value'] == 'http://www.w3.org/2000/01/rdf-schema#seeAlso':
				if '/instruments/' in x['oo']['value']:
					data_dict[x['s']['value']]['seealso'] = x['oo']['value']

	for x in data['vocab']:
		if x['p']['value'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
			onto_dict['type'] = x['o']['value']
		if x['p']['value'] == 'http://purl.org/dc/elements/1.1/creator':
			onto_dict['creator'] = x['o']['value']
		if x['p']['value'] == 'http://purl.org/dc/elements/1.1/description':
			onto_dict['desc'] = x['o']['value']
		if x['p']['value'] == 'http://purl.org/dc/terms/issued':
			onto_dict['issued'] = x['o']['value']
		if x['p']['value'] == 'http://purl.org/vocab/vann/preferredNamespacePrefix':
			onto_dict['prefix'] = x['o']['value']
		if x['p']['value'] == 'http://purl.org/vocab/vann/preferredNamespaceUri':
			onto_dict['namespace'] = x['o']['value']

	data_ary = []

	for x in data_dict:
		data_dict[x]['uri'] = x
		data_ary.append(data_dict[x])

	return {'roles':data_ary,'vocab':onto_dict}





"""
Returns the void
"""
def return_serialized_void(type):
	sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
	print(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD'])
	sparql.setCredentials(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD'])

	query = """
	    SELECT * WHERE
	    {
	        <http://data.carnegiehall.org/> ?p ?o .
	    }
	"""


	sparql.setQuery(query)

	g = Graph()
	dcterms = Namespace('http://purl.org/dc/terms/')
	foaf = Namespace('http://xmlns.com/foaf/0.1/')


	g.bind('dcterms', dcterms)
	g.bind('foaf', foaf)

	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	for result in results["results"]["bindings"]:
		if (result['o']['type'] == 'uri'):
			g.add( (URIRef("http://data.carnegiehall.org/"), URIRef(result['p']['value']) , URIRef(result['o']['value'])) )
		else:
			if 'datatype' in result['o']:
				g.add( (URIRef("http://data.carnegiehall.org/"), URIRef(result['p']['value']) , Literal(result['o']['value'], datatype=URIRef(result['o']['datatype']))) )
			else:
				g.add( (URIRef("http://data.carnegiehall.org/"), URIRef(result['p']['value']) , Literal(result['o']['value'])) )



	query = """
	    SELECT * WHERE
	    {
	        <http://carnegiehall.org/> ?p ?o .
	    }

	"""
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()



	for result in results["results"]["bindings"]:
		if (result['o']['type'] == 'uri'):
			g.add( (URIRef("http://carnegiehall.org/"), URIRef(result['p']['value']) , URIRef(result['o']['value'])) )
		else:
			if 'datatype' in result['o']:
				g.add( (URIRef("http://carnegiehall.org/"), URIRef(result['p']['value']) , Literal(result['o']['value'], datatype=URIRef(result['o']['datatype']))) )
			else:
				g.add( (URIRef("http://carnegiehall.org/"), URIRef(result['p']['value']) , Literal(result['o']['value'])) )






	if len(g) == 0:
		return '404'

	if (type == 'xml'):
		return g.serialize(format="xml")
	elif (type == 'n3'):
		return g.serialize(format="n3")
	elif (type == 'nt'):
		return g.serialize(format="nt")
	elif (type == 'turtle'):
		return g.serialize(format="turtle")
	elif (type == 'jsonld'):
		return g.serialize(format="json-ld")
	else:
		return g.serialize(format="nt")


"""
Returns entire roles vocab
"""
def return_serialized_vocabulary_role(type):

	sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
	sparql.setCredentials(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD'])


	object_data = {'roles':[],'vocab':[]}

	g = Graph()
	dcterms = Namespace('http://purl.org/dc/terms/')
	foaf = Namespace('http://xmlns.com/foaf/0.1/')
	vann = Namespace('http://purl.org/vocab/vann/')
	dc = Namespace('http://purl.org/dc/elements/1.1/')
	g.bind('dcterms', dcterms)
	g.bind('foaf', foaf)
	g.bind('vann', vann)
	g.bind('dc', dc)

	query = """
		SELECT * WHERE{
		  {
		    SELECT ?s WHERE{
		        ?s <http://www.w3.org/2000/01/rdf-schema#isDefinedBy> ?o .
		    }
		  }
		  ?s ?p ?oo .
		}
		ORDER BY ?s

	"""
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	object_data['roles'] = results["results"]["bindings"]
	for result in results["results"]["bindings"]:
		if (result['oo']['type'] == 'uri'):
			g.add( (URIRef(result['s']['value']), URIRef(result['p']['value']) , URIRef(result['oo']['value'])) )
		else:
			if 'datatype' in result['oo']:
				g.add( (URIRef(result['s']['value']), URIRef(result['p']['value']) , Literal(result['oo']['value'], datatype=URIRef(result['oo']['datatype']))) )
			else:
				g.add( (URIRef(result['s']['value']), URIRef(result['p']['value']) , Literal(result['oo']['value'])) )






	query = """
		SELECT * WHERE{
			<http://data.carnegiehall.org/vocabulary/roles/> ?p ?o.
		}

	"""



	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	object_data['vocab'] = results["results"]["bindings"]

	for result in results["results"]["bindings"]:
		if (result['o']['type'] == 'uri'):
			g.add( (URIRef("http://data.carnegiehall.org/vocabulary/roles/"), URIRef(result['p']['value']) , URIRef(result['o']['value'])) )
		else:
			if 'datatype' in result['o']:
				g.add( (URIRef("http://data.carnegiehall.org/vocabulary/roles/"), URIRef(result['p']['value']) , Literal(result['o']['value'], datatype=URIRef(result['o']['datatype']))) )
			else:
				g.add( (URIRef("http://data.carnegiehall.org/vocabulary/roles/"), URIRef(result['p']['value']) , Literal(result['o']['value'])) )





	if len(g) == 0:
		return '404'

	if (type == 'xml'):
		return g.serialize(format="xml")
	elif (type == 'n3'):
		return g.serialize(format="n3")
	elif (type == 'nt'):
		return g.serialize(format="nt")
	elif (type == 'turtle'):
		return g.serialize(format="turtle")
	elif (type == 'jsonld'):
		return g.serialize(format="json-ld")
	elif (type == 'data'):
		return object_data
	else:
		return g.serialize(format="nt")
