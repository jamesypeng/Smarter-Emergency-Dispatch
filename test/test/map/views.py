from django.shortcuts import render
from django.utils import timezone
from .models import *
from .forms import CurrentCallForm, CurrentAmbulanceForm

# Create your views here.

# VIEW USED FOR TESTING FORM BOX
# def current_state(request):
# 	form = CurrentCallForm()
# 	return render(request, 'map/current_state.html', {'form': form})



# WORKS WITH 'current_map' URL PATTERN
def current_map(request):
	if request.method == "POST":
		form = CurrentCallForm(request.POST, prefix='call')

		# Melanie added on 11/24
		form2 = CurrentAmbulanceForm(request.POST, prefix='amb')

		if form.is_valid():
			post = form.save(commit=False)
        	# call update current ems function

			#priya's changed
			l = Current_emscall()
			l.update_current_ems(post.addr)

			l.create_map()
			l.overwrite_map('./map/templates/map/map.html', './map/templates/map/map_test.html')

		# Melanie added on 11/24
		elif form2.is_valid():
			post2 = form2.save(commit=False)
			# post2.save()


	else:
		form = CurrentCallForm(prefix='call')
		form2 = CurrentAmbulanceForm(prefix='amb')


	return render(request, 'map/map_test.html', {'form': form, 'form2': form2 })
	# return render(request, 'map/map_test.html', extra_context)


def about(request):
	return render(request, 'map/about.html')