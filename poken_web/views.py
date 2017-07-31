# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
def index(request):

    context = {
        'name': 'Anwar'
    }

    return render(request, 'poken_web/index.html', context)
