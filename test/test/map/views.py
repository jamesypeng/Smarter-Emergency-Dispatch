from django.shortcuts import render
from django.utils import timezone
from .models import *
from .forms import CurrentCallForm

# Create your views here.

# VIEW USED FOR TESTING FORM BOX
# def current_state(request):
# 	form = CurrentCallForm()
# 	return render(request, 'map/current_state.html', {'form': form})



# WORKS WITH 'current_map' URL PATTERN
def current_map(request):
	if request.method == "POST":
		form = CurrentCallForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
        	# call update current ems function

			#priya's changed
			l = Current_emscall()
			l.update_current_ems(post.addr)

			l.create_map()
			l.overwrite_map('./map/templates/map.html', './map/templates/map_test.html')

			# post.LAT = 130.0
			# post.LONG = 35.0
			# post.time = timezone.now()
			# post.save()
            # return redirect('current_state', pk=post.pk)
	else:
		form = CurrentCallForm()
	return render(request, 'map/map_test.html', {'form': form})


