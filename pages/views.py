from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.defaulttags import register
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_sameorigin

from wagtail.core.models import Page
from wagtail.search.models import Query


from datetime import datetime, timedelta
import dateutil.parser
import folium
from folium.plugins import MarkerCluster
import json
from SPARQLWrapper import SPARQLWrapper, JSON

import os
env = os.environ.copy()

from .forms import YearForm
from .models import LabReport


@method_decorator(login_required, name='dispatch')
class LabReportCreateView(CreateView):
    model = LabReport
    template_name = 'labReport_create.html'
    fields = ('title', 'experiment_id', 'description', 'methods_intro', 'methods', 'query', 'conclusion_1', 'conclusion_2')
    success_url = reverse_lazy('labReport_list')

@method_decorator(login_required, name='dispatch')
class LabReportListView(ListView):

    model = LabReport
    template_name = 'labReport_list.html'
    context_object_name = 'labReports'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(LabReportListView, self).get_context_data(**kwargs)
        labReports = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(labReports, self.paginate_by)
        try:
            labReports = paginator.page(page)
        except PageNotAnInteger:
            labReports = paginator.page(1)
        except EmptyPage:
            labReports = paginator.page(paginator.num_pages)
        context['labReports'] = labReports
        return context

class LabReportDetailView(DetailView):

    model = LabReport
    template_name = 'labReport_detail.html'
    context_object_name = 'labReport'

# Create your views here.
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
# def index(request):
#     context = {"home_page": "active"}
#     return render(request, 'pages/index.html', context)
def experiments(request):
    context = {"experiments_page": "active"}
    return render(request, 'pages/experiments.html', context)
def about(request):
    context = {"about_page": "active"}
    return render(request, 'pages/about.html', context)
def contact(request):
    context = {"contact_page": "active"}
    return render(request, 'pages/contact.html', context)

def yearForm(request):
    submitted = False
    print(request)
    print('heeehhh')
    print(request.method)
    if request.method == 'POST':
        form = YearForm(request.POST)


        if form.is_valid():
            cd = form.cleaned_data   
            print(cd)         
            # assert False
            return HttpResponseRedirect('/datalab/experiments/chdl-0007?submitted=True')
    else:
        form = YearForm()
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'pages/yearForm.html', {'form': form, 'submitted': submitted})


# def button_chdl0007(request):
#     return render(request, 'pages/yearForm.html', context)
def beethovenCount(request):
    return render(request, 'pages/experiments/chdl-0002.html')
def firstVienneseSchool(request):
    return render(request, 'pages/experiments/chdl-0003.html')
def threeBs(request):
    return render(request, 'pages/experiments/chdl-0004.html')
def grammyWinners(request):
    return render(request, 'pages/experiments/chdl-0005.html')
def genreChart(request):
    return render(request, 'pages/experiments/chdl-0006.html')
def may5(request):
    return render(request, 'pages/experiments/chdl-0008.html')
def top25(request):
    return render(request, 'pages/experiments/chdl-0009.html')
def leschetizky(request):
    return render(request, 'pages/experiments/chdl-0010.html')
def button_chdl0011(request):
    return render(request, 'pages/experiments/chdl-0011.html')


@xframe_options_sameorigin
def chdl0001d(request):
    chBdays_GeoJSON = {}

    sparql = SPARQLWrapper(env['SPARQL_ENDPOINT'])
    sparql.setCredentials(env['SPARQL_USERNAME'], env['SPARQL_PASSWORD'])
    sparql.setQuery("""
        #Whose birthday is today? (for map)
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX schema: <http://schema.org/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX geo-pos: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?personName ?birthPlaceLabel ?lat ?long ?opasID ?wikidataLink (YEAR(?date) as ?year)
        (IRI(CONCAT("https://www.carnegiehall.org/About/History/Performance-History-Search?q=&dex=prod_PHS&pf=",
                      (STR(ENCODE_FOR_URI(?personName))))) AS ?perfLink)
        (IRI(CONCAT("https://www.carnegiehall.org/About/History/Performance-History-Search?q=&dex=prod_PHS&cmp=",
                      (STR(ENCODE_FOR_URI(?personName))))) AS ?compLink)
        WHERE
        {
            BIND(MONTH(NOW()) AS ?nowMonth)
            BIND(DAY(NOW()) AS ?nowDay)

            ?personID schema:birthDate ?date ;
                    foaf:name ?personName ;
                    dbo:birthPlace ?birthPlace .
            ?birthPlace rdfs:label ?birthPlaceLabel ;
                        geo-pos:lat ?lat ;
                        geo-pos:long ?long .
            OPTIONAL { ?personID skos:exactMatch ?wikidataLink .
                filter contains(str(?wikidataLink), "wikidata")}
            BIND(REPLACE(str(?personID), "http://data.carnegiehall.org/names/", "") as ?opasID)
            FILTER (MONTH(?date) = ?nowMonth && DAY(?date) = ?nowDay)

        }
        ORDER BY ?year
        LIMIT 100
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        name = result["personName"]["value"]
        opasID = result["opasID"]["value"]
        if int(opasID) > 1000000:
            phs = result["compLink"]["value"]
        else:
            phs = result["perfLink"]["value"]
        phsLink = "".join(['<h4>', '<a href="', phs,'"', ' target="_blank">', name, '</a>', '</h4>'])
        birthYear = result["year"]["value"]
        birthPlaceLabel = result["birthPlaceLabel"]["value"]
        birthInfo = "".join(['Born ', '<strong>', birthYear, '</strong>', ' in ', birthPlaceLabel, '</h3>'])
        lat = float(result["lat"]["value"])
        long = float(result["long"]["value"])
        coordinates = list([long, lat])
        try:
            wikidata = result["wikidataLink"]["value"]
        except:
            KeyError
            wikidata = ""

        if wikidata != "":
            wikidataLink = "".join(['<a href="', wikidata,'"', ' target="_blank">', 'Wikidata Item', '</a>'])
        else:
            wikidataLink = "<em>No Wikidata Item</em>"

        popupText = "".join([phsLink, '<br>', birthInfo, '<br>', wikidataLink])

        chBdays_GeoJSON[str(opasID)] = {}
        chBdays_GeoJSON[str(opasID)]["type"] = "Feature"
        chBdays_GeoJSON[str(opasID)]["properties"] = {}
        chBdays_GeoJSON[str(opasID)]["properties"]["name"] = popupText
        chBdays_GeoJSON[str(opasID)]["geometry"] = {}
        chBdays_GeoJSON[str(opasID)]["geometry"]["type"] = "Point"
        chBdays_GeoJSON[str(opasID)]["geometry"]["coordinates"] = coordinates


    if 'json' in request.GET:

        return JsonResponse(chBdays_GeoJSON, safe=False)


    data = chBdays_GeoJSON
    LONDON_COORDS = (51.5074, 0.1278)
    map = folium.Map(location=LONDON_COORDS, zoom_start=3)
    marker_cluster = MarkerCluster()

    for key in data:
        popupText = data[key]["properties"]["name"]
        long = data[key]["geometry"]["coordinates"][0]
        lat = data[key]["geometry"]["coordinates"][1]

        popup = folium.Popup(popupText, max_width=2650)
        # folium.Marker([lat, long], popup=popup).add_to(map)
        marker_cluster.add_child(folium.Marker([lat, long], popup=popup))

    map.add_child(marker_cluster)

    ## Option 1 saves map as iframe
    ## But __repr__html() wipes out special characters
    ## E.g. 'Nouguès' becomes 'NouguÃ¨s'
    ## To use, uncomment here and Option 1 for return
    # map = map._repr_html_()
    # context = {'my_map': map}

    ## Option 2 saves map to render in a new page
    ## It preserves special characters, e.g. 'Nouguès', but no nav
    ## To use, uncomment here and Option 2 for return
    map.save('pages/templates/pages/experiments/chdl-0001-d.html')

    # ## Option 1
    # return render(request, 'pages/experiments/chdl-0001-d.html', context)

    ## Option 2
    return render(request, 'pages/experiments/chdl-0001-d.html')



def chdl0001c(request):
    chBdays_GeoJSON = {}

    sparql = SPARQLWrapper(env['SPARQL_ENDPOINT'])
    sparql.setCredentials(env['SPARQL_USERNAME'], env['SPARQL_PASSWORD'])
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX schema: <http://schema.org/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX geo-pos: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?personName ?birthPlace ?birthPlaceLabel ?lat ?long ?opasID ?wikidataLink (YEAR(?date) as ?year)
        (IRI(CONCAT("https://www.carnegiehall.org/About/History/Performance-History-Search?q=&dex=prod_PHS&pf=",
                      (STR(ENCODE_FOR_URI(?personName))))) AS ?perfLink)
        (IRI(CONCAT("https://www.carnegiehall.org/About/History/Performance-History-Search?q=&dex=prod_PHS&cmp=",
                      (STR(ENCODE_FOR_URI(?personName))))) AS ?compLink)
        WHERE
        {
            BIND(MONTH(NOW()) AS ?nowMonth)
            BIND(DAY(NOW()) AS ?nowDay)

            ?personID schema:birthDate ?date ;
                    foaf:name ?personName ;
                    dbo:birthPlace ?birthPlace .
            ?birthPlace rdfs:label ?birthPlaceLabel ;
                        geo-pos:lat ?lat ;
                        geo-pos:long ?long .
            OPTIONAL { ?personID skos:exactMatch ?wikidataLink .
                filter contains(str(?wikidataLink), "wikidata")}
            BIND(REPLACE(str(?personID), "http://data.carnegiehall.org/names/", "") as ?opasID)
            FILTER (MONTH(?date) = ?nowMonth && DAY(?date) = ?nowDay)

        }
        ORDER BY ?year
        LIMIT 100
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        name = result["personName"]["value"]
        opasID = result["opasID"]["value"]
        if int(opasID) > 1000000:
            phsLink = result["compLink"]["value"]
        else:
            phsLink = result["perfLink"]["value"]
        birthYear = result["year"]["value"]
        birthPlace = result["birthPlace"]["value"]
        birthPlaceLabel = result["birthPlaceLabel"]["value"]
        lat = float(result["lat"]["value"])
        long = float(result["long"]["value"])
        coordinates = list([long, lat])
        try:
            wikidataLink = result["wikidataLink"]["value"]
        except:
            KeyError
            wikidataLink = ""


        chBdays_GeoJSON[str(opasID)] = {}
        chBdays_GeoJSON[str(opasID)]["type"] = "Feature"
        chBdays_GeoJSON[str(opasID)]["properties"] = {}
        chBdays_GeoJSON[str(opasID)]["properties"]["name"] = name
        chBdays_GeoJSON[str(opasID)]["properties"]["url"] = phsLink
        chBdays_GeoJSON[str(opasID)]["properties"]["wikidata"] = wikidataLink
        chBdays_GeoJSON[str(opasID)]["properties"]["date"] = birthYear
        chBdays_GeoJSON[str(opasID)]["properties"]["geobirth"] = birthPlace
        chBdays_GeoJSON[str(opasID)]["properties"]["city"] = birthPlaceLabel
        chBdays_GeoJSON[str(opasID)]["geometry"] = {}
        chBdays_GeoJSON[str(opasID)]["geometry"]["type"] = "Point"
        chBdays_GeoJSON[str(opasID)]["geometry"]["coordinates"] = coordinates

    data = chBdays_GeoJSON
    return render(request, 'pages/experiments/chdl-0001-c.html', {'data':data})

def chdl0007(request):
    year = request.POST['year']

    def get_next_weekday(startdate):
        """
        @startdate: given date, in format 'YYYY-MM-DD'
        """
        d = datetime.strptime(startdate, '%Y-%m-%d')
        t = timedelta((12 - d.weekday()) % 7)
        # t = timedelta((7 + weekday - d.weekday()) % 7)
        return (d + t).strftime('%Y-%m-%d')

    query = 'PREFIX dcterms: <http://purl.org/dc/terms/>'
    query = query + 'PREFIX event: <http://purl.org/NET/c4dm/event.owl#>'
    query = query + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>'
    query = query + 'select ?event ?title ?date ?venueName ?eventURL where {'
    query = query + 'BIND(YEAR(NOW()) AS ?nowYear)'
    query = query + 'BIND(MONTH(NOW()) AS ?nowMonth)'
    query = query + 'BIND(DAY(NOW()) AS ?nowDay)'
    query = query + '?event a event:Event ;'
    query = query + 'dcterms:date ?date ;'
    query = query + 'event:place ?venue ;'
    query = query + 'rdfs:label ?title .'
    query = query + '?venue rdfs:label ?venueName .'
    query = query + 'FILTER (YEAR(?date) = ' + year + ' && MONTH(?date) = ?nowMonth && DAY(?date) = ?nowDay)'
    query = query + '''BIND(IRI(REPLACE(str(?event), 'http://data.carnegiehall.org/events/', 'https://www.carnegiehall.org/About/History/Performance-History-Search?q=&dex=prod_PHS&event=')) AS ?eventURL).}'''
    query = query + 'ORDER BY ?date'

    sparql = SPARQLWrapper(env['SPARQL_ENDPOINT'])
    sparql.setCredentials(env['SPARQL_USERNAME'], env['SPARQL_PASSWORD'])
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    data = {}
    data['year'] = year

    try:
        for result in results["results"]["bindings"]:
            eventID = result["event"]["value"]
            eventURL = result["eventURL"]["value"]
            eventTitle = result["title"]["value"]
            eventDate = result["date"]["value"]
            venueName = result["venueName"]["value"]
            eventTime = dateutil.parser.isoparse(eventDate).strftime('%I:%M %p')
            displayDate = dateutil.parser.isoparse(eventDate).strftime('%A %B %-d, %Y')

            data['displayDate'] = displayDate
            data[str(eventID)] = {}
            data[str(eventID)]['eventURL'] = eventURL
            data[str(eventID)]['eventTitle'] = eventTitle
            data[str(eventID)]['eventTime'] = eventTime
            data[str(eventID)]['venueName'] = venueName

        eventDateTime = dateutil.parser.parse(results["results"]["bindings"][0]["date"]["value"])

        startdate = str(datetime.date(eventDateTime))

        hot100_date = get_next_weekday(startdate)
        hot100_URL = ''.join(['https://www.billboard.com/charts/hot-100/', hot100_date])

        data['hot100'] = hot100_URL

        # webbrowser.open(hot100_URL, new=2)
    except IndexError:
        messages.info(request, 'No events on this date at Carnegie Hall.')

    return render(request, 'pages/experiments/chdl-0007.html', {'data':data})

def chdl0011(request):
    def get_next_weekday(startdate):
          """
          @startdate: given date, in format 'YYYY-MM-DD'
          """
          d = datetime.strptime(startdate, '%Y-%m-%d')
          t = timedelta((12 - d.weekday()) % 7)
          return (d + t).strftime('%Y-%m-%d')

    query = 'PREFIX chgenres: <http://data.carnegiehall.org/genres/>'
    query = query + 'PREFIX dcterms: <http://purl.org/dc/terms/>'
    query = query + 'PREFIX event: <http://purl.org/NET/c4dm/event.owl#>'
    query = query + 'PREFIX foaf: <http://xmlns.com/foaf/0.1/>'
    query = query + 'PREFIX mo: <http://purl.org/ontology/mo/>'
    query = query + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>'
    query = query + 'PREFIX skos: <http://www.w3.org/2004/02/skos/core#>'
    query = query + 'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>'
    query = query + 'select distinct ?event (str(?label) AS ?eventTitle) ?date ?phsLink where {'
    query = query + '?event rdfs:label ?label ;'
    query = query + 'mo:genre chgenres:39 ;'
    query = query + 'dcterms:date ?date ;'
    query = query + 'event:place ?place .'
    query = query + '?place rdfs:label ?venueLabel .'
    query = query + '''BIND(IRI(REPLACE(str(?event), "http://data.carnegiehall.org/events/", "https://www.carnegiehall.org/About/History/Performance-History-Search?q=&dex=prod_PHS&event=")) AS ?phsLink).'''
    query = query + '''FILTER(?date >= xsd:dateTime("1971-09-01T00:00:00") && ?date <= xsd:dateTime("1972-09-01T00:00:00"))}'''
    query = query + 'ORDER BY ?date'

    sparql = SPARQLWrapper(env['SPARQL_ENDPOINT'])
    sparql.setCredentials(env['SPARQL_USERNAME'], env['SPARQL_PASSWORD'])
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    data = {}

    for result in results["results"]["bindings"]:
        eventID = result["event"]["value"]
        eventTitle = result["eventTitle"]["value"]
        eventDate = result["date"]["value"]
        href_phs = result["phsLink"]["value"]
        displayDate = dateutil.parser.isoparse(eventDate).strftime('%a %b %-d %Y at %-I%p')

        data[str(eventID)] = {}
        data[str(eventID)]['eventURL'] = href_phs
        data[str(eventID)]['eventTitle'] = eventTitle
        data[str(eventID)]['displayDate'] = displayDate

        eventDateTime = dateutil.parser.parse(eventDate)
        startdate = str(datetime.date(eventDateTime))
        hot100_date = get_next_weekday(startdate)
        href_hot100 = 'https://www.billboard.com/charts/hot-100/'
        hot100_formattedLink = f'{href_hot100}{hot100_date}'
        data[str(eventID)]['hot100'] = hot100_formattedLink

    return render(request, 'pages/experiments/chdl-0011.html', {'data':data})




def search(request):
    # Search
    search_query = request.GET.get('query', None)
    if search_query:
        search_results = Page.objects.live().search(search_query)

        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = Page.objects.none()

    # Render template

    if search_query == None:
        search_query = ''
        
    return render(request, 'search_results.html', {
        'search_query': search_query,
        'search_results': search_results,
    })
