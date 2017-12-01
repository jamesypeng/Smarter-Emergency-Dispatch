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

		# Melanie changed on 11/26
		if form.is_valid() and 'call_submit' in request.POST:
		# if "addr" in form.data.keys():
			post = form.save(commit=False)
        	# call update current ems function

			#priya's changed
			l = Current_emscall()
			l.update_current_ems(post.addr)

			k = Current_ambulance()
			k.dispatch_ambulance()

			k.update_amb_locs()

			l.create_map()
			l.overwrite_map('./map/templates/map/map.html', './map/templates/map/map_test.html')

		# Melanie added on 11/24
		elif form2.is_valid() and 'amb_submit' in request.POST:
			# post2 = form2.save(commit=False)

			# This is the ID input by the user
			input_id = form2['amb_id'].value()

			a = Current_ambulance()
			a.store_single_amb_record(input_id)

			# Argument for AVAILABLE becomes 1 since the ambulance is being put back in service
			a.update_amb_status_only(input_id,1)

			a.update_amb_locs()

			l = Current_emscall()
			l.create_map()
			l.overwrite_map('./map/templates/map/map.html', './map/templates/map/map_test.html')


	else:
		form = CurrentCallForm(prefix='call')
		form2 = CurrentAmbulanceForm(prefix='amb')


	# JASON: adding query to fill html table we are using as a feed to display
	# recent events for the user.
	## NOTE: initially testing with existing table. will need to replace this
	## with table name/fields from the events tracking table once we make it.
	recent_events_query = EMS_Calls.objects.all()[:5]

	return render(request, 'map/map_test.html', {'form': form, 'form2': form2,'recent_events_query':recent_events_query })
	# return render(request, 'map/map_test.html', extra_context)


def about(request):
	return render(request, 'map/about.html')
