from django.http import HttpResponse
from django.shortcuts import render
from game.forms import NameForm

def start_page(request):
    form = NameForm()
    context = {"form": form}
    return render(request, "start_page.html", context)