from __future__ import with_statement
from fabric.api import cd, settings, env, abort, local, run, get
from fabric.contrib.console import confirm

from datetime import datetime

env.hosts = ['ssh.alwaysdata.com']
env.user = 'feel'

def test():
    with settings(warn_only=True):
        result = local('./manage.py test travelapp', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def commit():
    local("git add -p && git commit")

def push():
    local("git push")

def prepare_deploy():
    test()
    commit()
    push()

def deploy():
    code_dir = '~/www/tb'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git://github.com/fsquillace/tb.git %s" % code_dir)
    with cd(code_dir):
        run("git pull")
        run('python manage.py collectstatic -v0 --noinput')
        run("touch tb/public/django.wsgi")
        
