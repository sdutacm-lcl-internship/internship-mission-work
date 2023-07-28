from datetime import datetime
from datetime import timedelta
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.http import JsonResponse
from django.http import HttpResponse
import json
from http.client import responses
from netrc import netrc
import requests
import json
import os
import re
from bs4 import BeautifulSoup
import lxml
import sys
import time
import json
#import models
import pytz


def acc():
    return HttpResponse("222")