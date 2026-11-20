from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from tasks.forms import ProjectForm, TaskForm
from tasks.models import Project, Task


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 5

    def get_queryset(self):
        queryset = Project.objects.all()
        self.search_query = self.request.GET.get("search", "").strip()
        if self.search_query:
            queryset = queryset.filter(
                Q(name__icontains=self.search_query)
                | Q(description__icontains=self.search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.search_query
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = self.object.tasks.filter(is_deleted=False).select_related(
            "task_type", "result"
        )
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("tasks:list")


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    context_object_name = "project"

    def get_success_url(self):
        return reverse_lazy("tasks:project_detail", kwargs={"pk": self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "projects/project_confirm_delete.html"
    success_url = reverse_lazy("tasks:list")


class ProjectTaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        form.instance.project = self.get_project()
        return super().form_valid(form)

    def get_project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.get_project()
        return context

    def get_success_url(self):
        return reverse_lazy(
            "tasks:project_detail", kwargs={"pk": self.get_project().pk}
        )
