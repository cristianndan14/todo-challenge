from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "task"
    template_name = "todo/task_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)

        search_title = self.request.GET.get('search-title') or ''
        filter_option = self.request.GET.get('filter-option') or ''
        today = datetime.now().date()

        if search_title:
            queryset = queryset.filter(title__icontains=search_title)

        if filter_option == 'today':
            queryset = queryset.filter(created__exact=today)

        if filter_option == 'yesterday':
            yesterday = today - timedelta(days=1)
            queryset = queryset.filter(created__exact=yesterday)

        if filter_option == 'last_7_days':
            seven_days_ago = today - timedelta(days=7)
            queryset = queryset.filter(created__gte=seven_days_ago, created__lte=datetime.now().date())

        if filter_option == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            queryset = queryset.filter(created__exact=tomorrow)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_title = self.request.GET.get('search-title', '')
        filter_option = self.request.GET.get('filter-option', '')

        context["count"] = context["task"].filter(complete=False).count()
        context["search_title"] = search_title
        context["filter_option"] = filter_option

        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"
    template_name = "todo/task.html"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ["title", "description", "complete", "created"]
    success_url = reverse_lazy("task-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ["title", "description", "complete", "created"]
    success_url = reverse_lazy("task-list")


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("task-list")


class CustomLoginView(LoginView):
    template_name = "todo/login.html"
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse_lazy("task-list")


class RegisterPageView(FormView):
    template_name = "todo/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("task-list")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("task-list")
        return super().get(*args, **kwargs)
