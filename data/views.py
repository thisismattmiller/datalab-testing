from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
import requests
from requests.auth import HTTPBasicAuth
import re
import os

from . import utils

limit_re = re.compile('LIMIT\s([0-9]+)', re.IGNORECASE)


content_type_map = {
	'xml' : 'text/xml',
	'turtle' : 'text/turtle',
	'jsonld' : 'application/ld+json',
	'n3' : 'text/n3',
	'nt' : 'text/plain',
}



@csrf_exempt
# def route_sparql(request):


# 	isKey = request.GET.get('key', False)

# 	if isKey != False:
# 		return HttpResponse(content="", status=200)
# 	else:
# 		template = loader.get_template('main/sparql.html')
# 		context = {
# 		    'data': None,
# 		}
# 		return HttpResponse(template.render(context, request))

@csrf_exempt
def route_sparql(request):


	if request.method == 'GET':
		template = loader.get_template('sparql.html')
		context = {
		    'data': None,
		    "sparql_page": "active",
		}
		return HttpResponse(template.render(context, request))

	elif request.method == 'POST':

		# query = request.body.decode('utf-8')

		# print(query)
		# if (len(request.body.decode('utf-8')) == 0):
		# 	query = request.GET.get('query', '')

		query = request.POST.get("query", "")


		

		# add a limit to it if there is not one yet
		re_match = limit_re.search(query)

		if re_match == None:
			query = query + ' LIMIT 10000'
		else:
			if int(re_match.group(1)) > 10000:
				query = query.replace(re_match.group(),'LIMIT 10000')

		r = requests.post(settings.SPARQL_ENDPOINT, auth=HTTPBasicAuth(os.environ['SPARQL_USERNAME'], os.environ['SPARQL_PASSWORD']), headers={"Accept":"application/sparql-results+json"}, data = {'query':query})
		# print(request.body.decode('utf-8'))
		if "MALFORMED QUERY: Encountered " in r.text:
			return HttpResponse(content=r.text, status=500)
		else:
			return HttpResponse(content=r.text, status=200)



def route_homepage(request):
		response = HttpResponse(content="",status=302)
		response["Location"] = '/datalab'		
		return response


def route_works(request, id):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/works/'+id+'/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/works/'+id+'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/works/'+id+'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/works/'+id+'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/works/'+id+'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/works/'+id+'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/works/'+id+'/about'
		return response

def about_works(request,id,type):

	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/works/%s>" % (id),type)
		if data == '404':
			raise Http404
		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_works_dict("<http://data.carnegiehall.org/works/%s>" % (id))
		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('works/works.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))


def route_vocab_role(request):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/about'
		return response

def about_vocab_role(request,type):

	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_vocabulary_role(type)
		if data == '404':
			raise Http404
		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_vocabulary_role_dict()
		# if data['total_triples'] == 0:
		# 	raise Http404

		template = loader.get_template('vocabulary/role.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))


def route_events(request, id):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/about'
		return response




def about_events(request,id,type):
	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/events/%s>" % (id),type)
		if data == '404':
			raise Http404

		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_events_dict("<http://data.carnegiehall.org/events/%s>" % (id))
		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('events/events.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))


def route_products(request, id,product_id):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/work_' + product_id + '/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/work_' + product_id +'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/work_' + product_id +'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/work_' + product_id +'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/work_' + product_id +'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/work_' + product_id +'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/events/'+id+'/work_' + product_id +'/about'
		return response





def about_products(request,id,product_id,type):
	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/events/%s/work_%s>" % (id,product_id),type)
		if data == '404':
			raise Http404

		return HttpResponse(content=data,  content_type=content_type_map[type], status=200)
	else:
		data = utils.format_product_dict("<http://data.carnegiehall.org/events/%s/work_%s>" % (id,product_id))
		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('events/products.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))




def route_venues(request, id):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/venues/'+id+'/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/venues/'+id+'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/venues/'+id+'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/venues/'+id+'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/venues/'+id+'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/venues/'+id+'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/venues/'+id+'/about'
		return response


def about_venues(request,id,type):
	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/venues/%s>" % (id),type)
		if data == '404':
			raise Http404

		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_venues_dict("<http://data.carnegiehall.org/venues/%s>" % (id))
		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('venues/venues.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))



def route_instruments(request, id):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/instruments/'+id+'/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/instruments/'+id+'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/instruments/'+id+'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/instruments/'+id+'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/instruments/'+id+'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/instruments/'+id+'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/instruments/'+id+'/about'
		return response


def about_instruments(request,id,type):
	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/instruments/%s>" % (id),type)
		if data == '404':
			raise Http404

		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_instruments_dict("<http://data.carnegiehall.org/instruments/%s>" % (id))


		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('instruments/instruments.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))

def route_genres(request, id):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/genres/'+id+'/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/genres/'+id+'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/genres/'+id+'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/genres/'+id+'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/genres/'+id+'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/genres/'+id+'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/genres/'+id+'/about'
		return response


def about_genres(request,id,type):
	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/genres/%s>" % (id),type)
		if data == '404':
			raise Http404

		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_genres_dict("<http://data.carnegiehall.org/genres/%s>" % (id))


		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('genres/genres.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))


def route_vocab_roles(request, id):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/'+id+'/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/'+id+'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/'+id+'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/'+id+'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/'+id+'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/'+id+'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/vocabulary/roles/'+id+'/about'
		return response


def about_vocab_roles(request,id,type):
	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/vocabulary/roles/%s>" % (id),type)
		if data == '404':
			raise Http404

		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_vocab_roles_dict("<http://data.carnegiehall.org/vocabulary/roles/%s>" % (id))
		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('roles/role.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))



def route_roles(request, id):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/roles/'+id+'/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/roles/'+id+'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/roles/'+id+'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/roles/'+id+'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/roles/'+id+'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/roles/'+id+'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/roles/'+id+'/about'
		return response

def about_roles(request,id,type):
	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/roles/%s>" % (id),type)
		if data == '404':
			raise Http404

		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_roles_dict("<http://data.carnegiehall.org/roles/%s>" % (id))
		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('roles/roles.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))

def route_ensembles(request, id):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/ensembles/'+id+'/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/ensembles/'+id+'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/ensembles/'+id+'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/ensembles/'+id+'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/ensembles/'+id+'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/ensembles/'+id+'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/ensembles/'+id+'/about'
		return response

def about_ensembles(request,id,type):
	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/ensembles/%s>" % (id),type)
		if data == '404':
			raise Http404

		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_ensembles_dict("<http://data.carnegiehall.org/ensembles/%s>" % (id))
		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('ensembles/ensembles.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))


def route_names(request, id):


	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/names/'+id+'/about'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/names/'+id+'/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/names/'+id+'/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/names/'+id+'/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/names/'+id+'/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/names/'+id+'/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/names/'+id+'/about'
		return response

def about_names(request,id,type):
	if type == 'xml'  or type == 'turtle' or type == 'jsonld' or type == 'n3' or type == 'nt':
		data = utils.return_serialized_subjects("<http://data.carnegiehall.org/names/%s>" % (id),type)
		if data == '404':
			raise Http404

		return HttpResponse(content=data, content_type=content_type_map[type], status=200)
	else:
		data = utils.format_names_dict("<http://data.carnegiehall.org/names/%s>" % (id))
		if data['total_triples'] == 0:
			raise Http404

		template = loader.get_template('names/names.html')
		context = {
		    'data': data,
		}
		return HttpResponse(template.render(context, request))



def route_void(request):
	if 'text/htm' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/void/turtle'
		return response
	elif 'application/json+ld' in request.META.get('HTTP_ACCEPT') or 'application/json' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/void/jsonld'
		return response
	elif 'text/plain' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/void/nt'
		return response
	elif 'application/x-turtle' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/void/turtle'
		return response
	elif 'text/rdf+n3' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/void/n3'
		return response
	elif 'application/rdf+xml' in request.META.get('HTTP_ACCEPT') or 'application/xml' in request.META.get('HTTP_ACCEPT'):
		response = HttpResponse(content="", status=303)
		response["Location"] = '/void/xml'
		return response
	else:
		response = HttpResponse(content="", status=303)
		response["Location"] = '/void/turtle'
		return response

def about_void(request,type):

	data = utils.return_serialized_void(type)
	if data == '404':
		raise Http404
	return HttpResponse(content=data, content_type=content_type_map[type], status=200)
