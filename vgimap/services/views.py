# Create your views here
from django.http import HttpResponse
from django.template import Context, loader
def opensearch(request):
    response = HttpResponse(mimetype='application/opensearchdescription+xml')
    t = loader.get_template('opensearch.xml')
    c = Context({})
    response.write(t.render(c))
    return response
