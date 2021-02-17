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


class ProjectGanttView(LoginRequiredMixin, View):
    template_name = 'projects/graph.html'

    def get(self, request, *args, **kwargs):
        project_list = []

        for project in Project.objects.all():
            proj_dict = {
                'start': str(project.start_date.date()),
                'end': str(project.end_date.date()),
                'name': project.name,
                'id': project.project_id,
                'progress': project.progress
            }
            if project.dependencies:
                proj_dict['dependencies'] = project.dependencies
            project_list.append(proj_dict)

        return render(request, self.template_name, {'projects':project_list})

