from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError


def index(request):
    if 'session_id' in request.session:
        session_id = request.session['session_id']
    else:
        return HttpResponseServerError('Session not valid') # TODO appropriate error handling


