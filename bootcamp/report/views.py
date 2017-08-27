import os
import time

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
# Create your views here.
# import word_report
from bootcamp.report import word_report

BASE_DIR =os.path.dirname(os.path.dirname(__file__))

@login_required
def index(request):

    # all_feeds = Feed.get_feeds()
    # paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    # feeds = paginator.page(1)
    # from_feed = -1
    # if feeds:
    #     from_feed = feeds[0].id
    # file_name = os.path.join(BASE_DIR, 'report', 'static', 'report', str(time.time()))
    file_name = os.path.join('report', 'static', 'report', str(time.time()))
    upload_file = os.path.join(BASE_DIR, file_name)
    print(upload_file)
    with open(upload_file, 'w') as f:
        f.write('abcd')
    print(settings.STATIC_URL)
    # print(settings.STATIC_URL)
    # return HttpResponse(upload_file)

    from django.utils.encoding import smart_str
    print(smart_str(upload_file))
    response = HttpResponse(open(upload_file),
        content_type='application/force-download')  # mimetype is replaced by content_type for django 1.7
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(upload_file)
    response['X-Sendfile'] = smart_str(upload_file)
    # return render(request, 'report/index.html',
    #               {'upload_file': file_name})
    return response


@login_required
def report(request):
    id = request.POST.get('id')
    # print(settings.STATIC_URL)
    # return HttpResponse(upload_file)

    from django.utils.encoding import smart_str
    # return render(request, 'report/index.html',
    #               {'upload_file': file_name})
    word_file = str(time.time())
    report_f = word_report.create_report(id,
                                         '/Users/lipidong/learn/python/bootcamp/bootcamp/report/templates/template.docx',
                                        '/Users/lipidong/', word_file)

    print('report_f', os.path.join('/Users/lipidong/', word_file))

    response = HttpResponse(report_f,
        content_type='application/force-download')  # mimetype is replaced by content_type for django 1.7
    response['Content-Disposition'] = 'attachment; filename=%s.docx' % smart_str(id)
    response['X-Sendfile'] = smart_str(os.path.join('/Users/lipidong/', word_file))
    return response


@login_required
def report_form(request):

    # print(settings.STATIC_URL)
    # return HttpResponse(upload_file)
    if request.method == 'GET':

        return render(request, 'report/form.html')
    elif request.method == 'POST':
        id = request.POST.get('id')
        # print(settings.STATIC_URL)
        # return HttpResponse(upload_file)

        from django.utils.encoding import smart_str
        # return render(request, 'report/index.html',
        #               {'upload_file': file_name})
        word_file = str(time.time())
        report_f = word_report.create_report(id,
                                             '/Users/lipidong/learn/python/bootcamp/bootcamp/report/templates/template.docx',
                                             '/Users/lipidong/', word_file)

        print('report_f', os.path.join('/Users/lipidong/', word_file))

        response = HttpResponse(report_f,
                                content_type='application/force-download')  # mimetype is replaced by content_type for django 1.7
        response['Content-Disposition'] = 'attachment; filename=%s.docx' % smart_str(id)
        response['X-Sendfile'] = smart_str(os.path.join('/Users/lipidong/', word_file))
        return response


