#coding=utf8

import os
import time
import json
from datetime import datetime
from commands import getstatusoutput

from django.db import models

class Task(models.Model):

    # hosts, like web_servers:host1 .
    inventories = models.TextField(null = False, blank = False)

    # 0, do not use sudo; 1, use sudo .
    sudo = models.BooleanField(default = True) 

    # for example: ansible web_servers -m shell -a 'du -sh /tmp'
    # the 'du -sh /tmp' is cmd here
    cmd = models.TextField(null = False, blank = False)

    # return code of this job
    rc = models.IntegerField(null = True) 

    start = models.DateTimeField(null = True)
    end = models.DateTimeField(null = True)

    @property
    def cmd_shell(self):
        option = self.sudo and '--sudo' or ''
        option += ' -f 20 -m shell'
        return 'ansible %s %s -a "%s"' % (self.inventories, option, self.cmd)

    def run(self):
        if os.fork() == 0:
        #if 0 == 0:
            self.start = datetime.now()
            self.save()

            # initial jobs
            cmd_shell = self.cmd_shell + ' --list-hosts'
            status, output = getstatusoutput(cmd_shell)
            hosts = map(str.strip, output.splitlines())
            for host in hosts:
                self.job_set.add(Job(host = host, cmd = self.cmd))

            # run ansible
            tmpdir = '/tmp/ansible_%s' % self.id
            os.mkdir(tmpdir)
            cmd_shell = self.cmd_shell + ' -t ' + tmpdir
            status, output = getstatusoutput(cmd_shell)

            self.rc = status
            self.end = datetime.now()
            
            for f in os.listdir(tmpdir):
                result = json.loads(open(tmpdir + '/' + f).read())
                job = self.job_set.get(host = f)
                job.start = result.get('start')
                job.end = result.get('end')
                job.rc = result.get('rc')
                job.stdout = result.get('stdout')
                job.stderr = result.get('stderr')
                job.save()

            self.save()

            # clean tmp dir
            os.system('rm -rf ' + tmpdir)

    def __unicode__(self):
        return self.cmd_shell

class Job(models.Model):
    task = models.ForeignKey(Task)
    host = models.TextField(null = False, blank = False)
    cmd = models.TextField(null = False, blank = False)
    start = models.DateTimeField(null = True)
    end = models.DateTimeField(null = True)
    rc = models.IntegerField(null = True) 
    stdout = models.TextField(null = True)
    stderr = models.TextField(null = True)

    def __unicode__(self):
        return self.host + ' : ' + self.cmd


