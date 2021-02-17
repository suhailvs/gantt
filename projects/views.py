from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib import messages
from django.views import View

from projects.models import Project
from authentication.mixins import CreatorRequiredMixin


def home(request):
    if not request.user.is_authenticated: 
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin:index')

    if request.user.is_creator:
        pass

    return redirect('projects:project_list')

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project


class ProjectCreateView(CreatorRequiredMixin, CreateView):
    model = Project
    fields = ('project_id', 'name', 'start_date', 'end_date', 'progress','dependencies')
    template_name = 'projects/project_add_form.html'

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        messages.success(self.request, 'The project was created with success!')
        return redirect('projects:project_list')


class ProjectGanttView(CreatorRequiredMixin, View):
    template_name = 'projects/graph.html'

    def get(self, request, *args, **kwargs):
        project_list = []

        for project in Project.objects.all():
            project_list.append({
                'start': str(project.start_date.date()),
                'end': str(project.end_date.date()),
                'name': project.name,
                'id': project.project_id,
                'progress': project.progress
            })

        projects = [
            {
                'start': '2018-10-01',
                'end': '2018-10-08',
                'name': 'Redesign website',
                'id': "Task 0",
                'progress': 20
            },
            {
                'start': '2018-10-03',
                'end': '2018-10-06',
                'name': 'Write new content',
                'id': "Task 1",
                'progress': 5,
                'dependencies': 'Task 0'
            },
            {
                'start': '2018-10-04',
                'end': '2018-10-08',
                'name': 'Apply new styles',
                'id': "Task 2",
                'progress': 10,
                'dependencies': 'Task 1'
            },
            {
                'start': '2018-10-08',
                'end': '2018-10-09',
                'name': 'Review',
                'id': "Task 3",
                'progress': 5,
                'dependencies': 'Task 2'
            },
            {
                'start': '2018-10-08',
                'end': '2018-10-10',
                'name': 'Deploy',
                'id': "Task 4",
                'progress': 0,
                'dependencies': 'Task 2'
            },
            {
                'start': '2018-10-11',
                'end': '2018-10-11',
                'name': 'Go Live!',
                'id': "Task 5",
                'progress': 0,
                'dependencies': 'Task 4',
                'custom_class': 'bar-milestone'
            }
        ]
        return render(request, self.template_name, {'projects':project_list})

