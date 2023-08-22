import dtlpy as dl
import build_app
import subprocess

env = 'rc'
dl.setenv(env)
# project = dl.projects.get(project_id='f7d43fec-2823-4871-b0a0-1b76a75a2d61')  # Active Learning


project = dl.projects.get('feature vectors')



dpk = dl.dpks.get(dpk_name='active-learning-1.3')
project.apps.install(dpk=dpk)

app = project.apps.get(app_name='active-learning-1.3')
app.uninstall()



