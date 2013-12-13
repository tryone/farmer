#coding=utf8
from __future__ import with_statement

import os
import time
import json
from tempfile import mkdtemp
from datetime import datetime
from commands import getstatusoutput

from django.db import models

class Job(models.Model):

    # hosts, like web_servers:host1 .
    inventories = models.TextField(null = False, blank = False)

    # 0, do not use sudo; 1, use sudo .
    sudo = models.BooleanField(default = True)

    # for example: ansible web_servers -m shell -a 'du -sh /tmp'
    # the 'du -sh /tmp' is cmd here
    cmd = models.TextField(null = False, blank = False)

    # return code of this job
    rc = models.IntegerField(null = True)

    result = models.TextField(null = True)

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
            tmpdir =  mkdtemp(prefix='ansible_', dir='/tmp')
            self.start = datetime.now()
            self.save()
            cmd_shell = self.cmd_shell + ' -t ' + tmpdir
            status, output = getstatusoutput(cmd_shell)
            self.end = datetime.now()
            result = {}
            for f in os.listdir(tmpdir):
                with open(os.path.join(tmpdir, f)) as rf:
                    result[f] = json.loads(rf.read())
            self.rc = status
            self.result = json.dumps(result)
            self.save()
            os.removedirs(tmpdir)

    def __unicode__(self):
        return self.cmd_shell
