from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import GeneralForm

from utils.parameterParser import parseParameters
import action_scripts as actions
import json

from utils.miscellaneous import validate_request_session


def index(request):
    if validate_request_session(request):
        return HttpResponse("No action selected")
    else:
        return HttpResponseServerError('Session not valid')


@csrf_exempt
def execute(request, action_name):
    if validate_request_session(request):
        session_id = request.session['session_id']
        if request.method == 'POST':
            try:
                parameters = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                try:
                    parameters = json.loads(request.FILES['parameters'].read())
                except json.JSONDecodeError:
                    return HttpResponseServerError("Parameters not valid json")

            parsed_parameters = parseParameters(parameters, session_id=session_id)
            action_script_method = getattr(actions, action_name)
            action_result = action_script_method(parameters=parsed_parameters, session_id=session_id)
            # TODO write result class
            if action_result == 0:
                return HttpResponseRedirect('/')
            else:
                return HttpResponseServerError("Action failed")
        else:
            form = GeneralForm()
            return render(request, 'form.html', {'form': form})
    else:
        return HttpResponseServerError('Session not valid')
