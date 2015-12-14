import os

from paver.tasks import task, BuildFailure
from paver.easy import *


@task
def unit_tests():
    if os.path.exists('.coverage'):
        sh('rm .coverage')

    sh('nosetests --with-coverage --cover-html')


@task
def run_pylint():
    try:
        sh('pylint --msg-template="{path}:{line}: [{msg_id}] {msg}" '
           'metrics_app > pylint.txt')
    except BuildFailure:
        pass


@task
@needs('unit_tests', 'run_pylint')
def default():
    pass
