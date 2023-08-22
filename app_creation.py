import dtlpy as dl
import build_app
import subprocess

# build_app.main()

env = 'new-dev'
dl.setenv(env)
# project = dl.projects.get(project_id='f7d43fec-2823-4871-b0a0-1b76a75a2d61')  # Active Learning
# dpk = dl.dpks.get(dpk_name='active-learning-2', dpk_version='1.2.28')

# project = dl.projects.get('Active Learning 1.3')
# project = dl.projects.get('Model mgmt demo')
project = dl.projects.get('Active Learning')

# bump patch version
subprocess.check_call('bumpversion patch --allow-dirty', shell=True)

# publish dpk to app store
dpk = project.dpks.publish()

# install app in project
######################
###### THIS DOESNT WORK - https://dataloop.atlassian.net/browse/DAT-46413
# app = project.apps.get(app_id='646e065005efd71a305377f4')
app = project.apps.get(app_name='active-learning-1.3')
app.dpk_version = dpk.version
app.update()

######################
# app = project.apps.get(app_name=dpk.name)
# # app = project.apps.get(app_name='active-learning-1.3')
# app.uninstall()
# project.apps.install(dpk=dpk)


def clean_apps():
    for app in project.apps.list().all():
        try:
            print(app.name)
            app.uninstall()
        except Exception:
            ...


def clean_dpks():
    dpks = dl.dpks.list().all()
    for dpk in dpks:
        print(dpk.name)
        if dpk.name in ['active-learning',
                        'active-learning1',
                        'active-learning2',
                        'active-learning-with-compare',
                        'active-learning-yaya',
                        'active-learning-franch',
                        'franch-learner',
                        'scoring-and-metrics1']:
            filters = dl.Filters(field='dpkName', values=dpk.name, resource='apps')
            for app in dl.apps.list(filters=filters).all():
                print(app.name)
                app.uninstall()
            dpk.delete()


def clean_models():
    models = project.models.list().all()
    for model in models:
        print(model.name, model.creator)
        if model.creator == 'bot.4dc6041c-1fa2-42d4-81c9-8391f47f55b9@bot.dataloop.ai':
            print(model.name)
            model.delete()
