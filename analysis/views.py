from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from .models import Analysis
from .forms import AnalysisForm
from django.contrib import messages
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
import subprocess, os


def analysis_index(request):
    file_list = Analysis.objects.all()

    query = request.GET.get('q')
    if query:
        file_list = file_list.filter(file__icontains=query)

    paginator = Paginator(file_list, 20)  # Show 20 uploads per page

    page = request.GET.get('page')
    try:
        uploads = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        uploads = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        uploads = paginator.page(paginator.num_pages)

    return render(request, 'analysis/index.html', {'uploads': uploads})


def analysis_detail(request, id):
    analyzed = get_object_or_404(Analysis, id=id)
    url = request.get_full_path()
    if url.find("index") == 1:
        result_file_path = os.path.join(settings.BASE_DIR, 'results', analyzed.file.name)
        with open(result_file_path, "r") as f:
            results = f.read()
    else:
        results = subprocess_script(analyzed.file.url)
        result_file_path = os.path.join(settings.BASE_DIR, 'results', analyzed.file.name)
        with open(result_file_path, "w") as f:
            f.write(results)

    if results[:-1] == "exit":
        context = {
            'analyzed': analyzed,
            'failed': 'failed',
        }
    elif results[:-1] == "[]":
        context = {
            'analyzed': analyzed,
            'empty': 'empty',
        }


    else:
        results = results[2:-3].split("}, {")
        query = request.GET.get('q')
        if query:
            results = [k for k in results if query in k]

        res = []
        for i in results:
            i = "{" + i + "}"
            i2 = eval(i)
            res.append(i2)
        results = res

        context = {
            'analyzed': analyzed,
            'results': results,
        }

    return render(request, 'analysis/detail.html', context)


def analysis_create(request):
    form = AnalysisForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        analysis = form.save()
        return HttpResponseRedirect(analysis.get_absolute_url())

    context = {
        'form': form,
    }
    return render(request, 'home.html', context)


def subprocess_script( file_from_form ):
    sample_path = settings.BASE_DIR / file_from_form[1:]
    try:
        output = subprocess.run([settings.BASE_DIR / 'analysis.py', sample_path], capture_output=True, text=True)
        stdout = output.stdout
    except Exception as e:
        stdout = "exit\n"
    return stdout








