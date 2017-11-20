from django.shortcuts import render
from django.utils import timezone
from .models import Current_emscall
from .forms import CurrentCallForm

# Create your views here.

# VIEW USED FOR TESTING FORM BOX
# def current_state(request):
# 	form = CurrentCallForm()
# 	return render(request, 'map/current_state.html', {'form': form})



# WORKS WITH 'current_state' URL PATTERN
# def current_state(request):
#     if request.method == "POST":
#         form = CurrentCallForm(request.POST)
#         if form.is_valid():

#         	# call update current ems function

#             post = form.save(commit=False)
#             post.LAT = 130.0
#             post.LONG = 35.0
#             post.time = timezone.now()
#             post.save()
#             # return redirect('current_state', pk=post.pk)
#     else:
#         form = CurrentCallForm()
#     return render(request, 'map/current_state.html', {'form': form})


# WORKS WITH 'current_map' URL PATTERN
def current_map(request):
	if request.method == "POST":
		form = CurrentCallForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
        	# call update current ems function
			Current_emscall.update_current_ems(Current_emscall, post.addr)

			# post.LAT = 130.0
			# post.LONG = 35.0
			# post.time = timezone.now()
			# post.save()
            # return redirect('current_state', pk=post.pk)
	else:
		form = CurrentCallForm()
	return render(request, 'map/map_test.html', {'form': form})


