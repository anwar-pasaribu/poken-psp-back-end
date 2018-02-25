# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from django.shortcuts import render


# Create your views here.
from poken_rest.firebase import firebase_auth


def index(request):

    admin_url = request.build_absolute_uri("admin")
    print("Admin url: {0}".format(admin_url))

    context = {
        'name': 'Anwar',
        'fcm_response': '%s' % "asa"
    }

    return render(request, 'poken_web/index.html', context)
