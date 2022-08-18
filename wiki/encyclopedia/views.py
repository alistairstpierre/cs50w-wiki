from ast import MatchSequence
from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
import os

import markdown

from . import util

class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Search Encylopedia'}))

class CreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Page Title'}))
    md = forms.CharField(widget=forms.Textarea(attrs={'name':'body', 'style': 'height: 3em;', 'placeholder': 'Write your markdown here'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def create(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            md = form.cleaned_data["md"]
            if util.get_entry(title) != None:
                return render(request, "encyclopedia/create.html", {
                    "createForm": CreateForm(),
                    "message": f"The {title} page already exists"
                })
            else:
                util.save_entry(title, md)
                return HttpResponseRedirect(f"{title}")
        else:
            for field in form:
                print("Field Error:", field.name,  field.errors)

    return render(request, "encyclopedia/create.html", {
        "createForm": CreateForm()
    })

def entry(request, title):
    entry = util.get_entry(title)
    if entry == None:
        return render(request, "encyclopedia/page_not_found.html")
    md = markdown.markdown(entry)
    return render(request, "encyclopedia/entry.html", {
        "entry": md,
        "title": title,
        "form": SearchForm()
    })

def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            substring = form.cleaned_data["search"]
            entries = util.list_entries()
            if util.get_entry(substring) != None:
                return HttpResponseRedirect(f"{substring.lower()}")
            strings = list(filter(lambda s: (substring.lower() in s.lower()), entries))
            if len(strings) > 0:
                return render(request, "encyclopedia/search_results.html" , {
                    "results": strings
                })
            return render(request, "encyclopedia/page_not_found.html")
    return render(request, "encyclopedia/page_not_found.html")

