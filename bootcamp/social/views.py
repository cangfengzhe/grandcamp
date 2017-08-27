import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden)
from django.shortcuts import get_object_or_404, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
# Create your views here.

@login_required
def social(request):
    # all_feeds = Feed.get_feeds()
    # paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    # feeds = paginator.page(1)
    # from_feed = -1
    # if feeds:
    #     from_feed = feeds[0].id
    return HttpResponse('hahah')
