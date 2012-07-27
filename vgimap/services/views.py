# Create your views here
from django.shortcuts import render_to_response
def opensearch(request):
  return render_to_response('opensearch.xml')
