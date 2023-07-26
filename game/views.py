from django.shortcuts import render, redirect
from .forms import NameForm
from .models import Player
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.


def question_page_view(request):
    form = NameForm(request.POST or None)
    if (not form.is_valid()):
        return redirect("/")

    name = form.cleaned_data["username"]
    if (Player.objects.filter(username=data).count() == 0):
        print("creating")
        Player.objects.create(username=name)
    
    context = {"username": name}
    return render(request, "main_question.html", context)



@staff_member_required
def admin_panel_view(request):
    context = {}
    return render(request, "admin_panel.html", context)