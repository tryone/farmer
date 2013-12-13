
import json

from django.shortcuts import render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required

from farmer.models import Task, Job

@staff_member_required
def home(request):
    if request.method == 'POST':
        inventories = request.POST.get('inventories', '')
        cmd = request.POST.get('cmd', '')
        if '' in [inventories.strip(), cmd.strip()]:
            return redirect('/')
        task = Task()
        task.inventories = inventories
        task.cmd = cmd
        task.run()
        return redirect('/')
    else:
        tasks = Task.objects.all().order_by('-id')
        return render_to_response('home.html', locals())

@staff_member_required
def detail(request, id):
    assert(request.method == 'GET')
    jobid = request.GET.get('jobid', '')
    if jobid.isdigit():
        jobid = int(jobid)
    else:
        jobid = -1
    task = Task.objects.get(id = id)
    jobs = task.job_set.all().order_by('-rc')
    return render_to_response('detail.html', locals())

@staff_member_required
def retry(request, id):
    assert(request.method == 'GET')
    task = Task.objects.get(id = id)
    failure_hosts = [job.host for job in task.job_set.all() if job.rc]
    assert(failure_hosts)
    newtask = Task()
    newtask.inventories = ':'.join(failure_hosts)
    newtask.cmd = task.cmd
    newtask.run()
    return redirect('/')

@staff_member_required
def rerun(request, id):
    assert(request.method == 'GET')
    task = Task.objects.get(id = id)
    newtask = Task()
    newtask.inventories = task.inventories
    newtask.cmd = task.cmd
    newtask.run()
    return redirect('/')



