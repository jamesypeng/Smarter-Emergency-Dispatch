from django.shortcuts import render

# Create your views here.

def current_state(request):
    return render(request, 'map/current_state.html')

