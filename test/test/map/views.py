from django.shortcuts import render
from django.utils import timezone
from .models import Current_emscall
from .forms import CurrentCallForm

# Create your views here.

def current_state(request):
	form = CurrentCallForm()
	return render(request, 'map/current_state.html', {'form': form})

# def current_state(request):
# 	if request.method == "POST":
# 		form = CurrentCallForm(request.POST)
# 		if form.is_valid():
# 			call = form.save(commit=False)
# 			call.time = timezone.now()
# 			call.save()




# def post_new(request):
#     if request.method == "POST":
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user
#             post.published_date = timezone.now()
#             post.save()
#             return redirect('post_detail', pk=post.pk)
#     else:
#         form = PostForm()
#     return render(request, 'blog/post_edit.html', {'form': form})

