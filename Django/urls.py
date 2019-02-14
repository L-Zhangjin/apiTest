"""Django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django_web import views
from bugStatistics.stViews import bugStView
from django.conf.urls import include
from django_web.api import projectView, envView, apiView,caseView,caseApiView,taskView,reportView
from django.views import static
from django.conf import settings


handler403 = views.permission_denied
handler404 = views.page_not_found
handler500 = views.page_error

urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^django_web/', include('django_web.urls')),
    url(r'^bugStatistics/', include('bugStatistics.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^index/$', views.index),
    url(r'^welcom/$', views.welcom),
    url(r'^login_action/$', views.login_action),
    url(r'^login/$', views.login),
    url(r'^loginout/$', views.loginout),

    #user
    url(r'^user/$', views.userManager, name='user'),
    url(r'^userList/$', views.getUserList, name='userList'),
    url(r'^searchUser/$', views.searchUser, name='searchUser'),
    url(r'^userAdd/$', views.userAdd, name='userAdd'),
    url(r'^userPost/$', views.userPost, name='userPost'),
    url(r'^userEdit/(?P<uid>\d+)$', views.userEdit),
    url(r'^userDelete/$', views.userDelete, name='userDelete'),
    url(r'^userEditPost/$', views.userEditPost, name='userEditPost'),

    #project
    url(r'^project_index/$', projectView.project_index, name='project_index'),
    url(r'^projectList/$', projectView.getProjectList, name='projectList'),
    url(r'^projectAdd/$', projectView.projectAdd, name='projectAdd'),
    url(r'^projectAddPost/$', projectView.projectAddPost, name='projectAddPost'),
    url(r'^projectEdit/(?P<pid>\d+)$', projectView.projectEdit, name='projectEdit'),
    url(r'^projectEditPost/$', projectView.projectEditPost, name='projectEditPost'),
    url(r'^projectDelete/$', projectView.projectDelete, name='projectDelete'),

    #env
    url(r'^env_index/$', envView.env_index, name='env_index'),
    url(r'^evnList/$', envView.getEvnList, name='evnList'),
    url(r'^evnAdd/$', envView.evnAdd, name='evnAdd'),
    url(r'^selectProjectName/$', envView.selectProjectName, name='selectProjectName'),
    url(r'^envAddPost/$', envView.envAddPost, name='envAddPost'),
    url(r'^envEdit/(?P<eid>\d+)$', envView.envEdit, name='envEdit'),
    url(r'^envEditPost/$', envView.envEditPost, name='envEditPost'),
    url(r'^envDelete/$', envView.envDelete, name='envDelete'),

    #apicase
    url(r'^api_index/$', apiView.api_index, name='api_index'),
    url(r'^apiList/$', apiView.getApiList, name='apiList'),
    url(r'^apiAdd/$', apiView.apiAdd, name='apiAdd'),
    url(r'^apiAddPost/$', apiView.apiAddPost, name='apiAddPost'),
    url(r'^apiEdit/(?P<aid>\d+)$', apiView.apiEdit, name='apiEdit'),
    url(r'^apiDetail/(?P<pid>\d+)$', apiView.apiDetail, name='apiDetail'),
    url(r'^apiDelete/$', apiView.apiDelete, name='apiDelete'),
    url(r'^apiEditPost/$', apiView.apiEditPost, name='apiEditPost'),
    url(r'^simpleRun/(?P<pid>\d+)$', apiView.simpleRun, name='simpleRun'),
    url(r'^apiSimpleRun/$', apiView.apiSimpleRun, name='apiSimpleRun'),
    url(r'^selectEnvName/(?P<eid>\d+)$', apiView.selectEnvName, name='selectEnvName'),
    url(r'^copyApi/(?P<pid>\d+)$', apiView.copyApi, name='copyApi'),
    url(r'^apiCopyPost/$', apiView.apiCopyPost, name='apiCopyPost'),

    #case
    url(r'^apiCase_index/$', caseView.apiCase_index, name='apiCopyPost'),
    url(r'^caseList/$', caseView.getCaseList, name='caseList'),
    url(r'^caseAdd/$', caseView.caseAdd, name='caseAdd'),
    url(r'^caseAddPost/$', caseView.caseAddPost, name='caseAddPost'),
    url(r'^caseEdit/(?P<eid>\d+)$', caseView.caseEdit, name='caseEdit'),
    url(r'^caseEditPost/$', caseView.caseEditPost, name='caseEditPost'),
    url(r'^caseDelete/$', caseView.caseDelete, name='caseDelete'),
    url(r'^caseTask/(?P<caseData>.*)$', caseView.caseTask, name='caseTask'),


    #caseApi
    url(r'^caseApi/(?P<id>\d+)$', caseApiView.caseApi, name='caseApi'),
    url(r'^caseApiList/$', caseApiView.getCaseApiList, name='caseApiList'),
    url(r'^caseApiAdd/(?P<caseId>\d+)$', caseApiView.caseApiAdd, name='caseApiAdd'),
    url(r'^caseApiAddOld/(?P<caseId>\d+)$', caseApiView.caseApiAddOld, name='caseApiAddOld'),
    url(r'^caseApiAddPost/$', caseApiView.caseApiAddPost, name='caseApiAddPost'),
    url(r'^caseApiAddOldPost/(?P<caseId>\d+)$', caseApiView.caseApiAddOldPost, name='caseApiAddOldPost'),
    url(r'^apiListForProject/$', caseApiView.apiListForProject, name='apiListForProject'),
    url(r'^caseApiEdit/(?P<eid>\d+)$', caseApiView.caseApiEdit, name='caseApiEdit'),
    url(r'^caseApiDelete/$', caseApiView.caseApiDelete, name='caseApiDelete'),
    url(r'^caseApiMultRun/(?P<eid>\d+)$', caseApiView.caseApiMultRun, name='caseApiMultRun'),
    url(r'^caseApiEditPost/$', caseApiView.caseApiEditPost, name='caseApiEditPost'),
    url(r'^selectApiEnvName/$', caseApiView.selectApiEnvName, name='selectApiEnvName'),
    url(r'^autoApiSimpleRun/$', caseApiView.autoApiSimpleRun, name='autoApiSimpleRun'),

    #task
    url(r'^task_index/$', taskView.task_index, name='task_index'),
    url(r'^taskList/$', taskView.taskList, name='taskList'),
    url(r'^taskDelete/$', taskView.taskDelete, name='taskDelete'),
    url(r'^removeTask/$', taskView.removeTask, name='removeTask'),
    url(r'^taskRun/$', taskView.taskRun, name='taskRun'),
    url(r'^taskPause/$', taskView.taskPause, name='taskPause'),
    url(r'^caseTaskPost/$', taskView.caseTaskPost, name='caseTaskPost'),
    url(r'^taskResume/$', taskView.taskResume, name='taskResume'),
    url(r'^taskEdit/(?P<tid>\d+)$', taskView.taskEdit, name='taskEdit'),
    url(r'^tResult/(?P<autoRuntimeid>\d+)$', taskView.tResult, name='tResult'),
    url(r'^taskDetail/(?P<tid>\d+)$', taskView.taskDetail, name='taskDetail'),
    url(r'^taskLogList/(?P<tid>\d+)$', taskView.taskLogList, name='taskLogList'),

    #report
    url(r'^resuLtList/(?P<autoRuntimeid>\d+)$', reportView.resuLtList, name='resuLtList'),
    url(r'^rDetail/(?P<apiData>.*)$', reportView.rDetail, name='rDetail'),





    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static'),


]
