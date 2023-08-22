import dtlpy as dl
import build_app
import subprocess

# build_app.main()

# bump patch version
subprocess.check_call('bumpversion patch --allow-dirty', shell=True)

envs = ['rc', 'prod', 'new-dev']
project_names = ['Active Learning 1.3', 'Dataloop demo 2023', 'Active Learning']

for i, env in enumerate(envs):
    dl.setenv(env)
    if dl.token_expired():
        dl.login()

    project = dl.projects.get(project_names[i])

    # publish dpk to app store
    dpk = project.dpks.publish()

    # install app in project
    try:
        ######################
        # app = project.apps.get(app_id='646e065005efd71a305377f4')
        app = project.apps.get(app_name='active-learning-1.3')
        app.dpk_version = dpk.version
        app.update()
    except dl.exceptions.NotFound:
        app = project.apps.install(app_name='active-learning-1.3', dpk=dpk)

    ######################
    # app = project.apps.get(app_name=dpk.name)
    # # app = project.apps.get(app_name='active-learning-1.3')
    # app.uninstall()
    # project.apps.install(dpk=dpk)
