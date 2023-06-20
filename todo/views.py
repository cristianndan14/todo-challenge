from datetime import datetime, timedelta

from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = context["task"].filter(user=self.request.user)
        context["count"] = context["task"].filter(complete=False).count()
        
        search_title = self.request.GET.get('search-title') or ''
        filter_option = self.request.GET.get('filter-option') or ''
        
        if search_title:
            context['task'] = context['task'].filter(title__icontains=search_title)
            context['search_title'] = search_title
        
        if filter_option == 'today':
            today = datetime.now()
            start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)
            end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59)
            context['task'] = context['task'].filter(created__range=(start_of_day, end_of_day))
            context['filter_option'] = 'today'
        
        if filter_option == 'yesterday':
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            start_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
            end_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
            context['task'] = context['task'].filter(created__range=(start_of_day, end_of_day))
            context['filter_option'] = 'yesterday'
        
        if filter_option == 'last_7_days':
            today = datetime.now()
            seven_days_ago = today - timedelta(days=7)
            start_of_day = datetime(seven_days_ago.year, seven_days_ago.month, seven_days_ago.day, 0, 0, 0)
            end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59)
            context['task'] = context['task'].filter(created__range=(start_of_day, end_of_day))
            context['filter_option'] = 'last_7_days'
        
        if filter_option == 'tomorrow':
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            start_of_day = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
            end_of_day = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59)
            context['task'] = context['task'].filter(created__range=(start_of_day, end_of_day))
            context['filter_option'] = 'tomorrow'
        
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"
    template_name = "todo/task.html"


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ["title", "description", "complete", "created"]
    success_url = reverse_lazy("task")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ["title", "description", "complete", "created"]
    success_url = reverse_lazy("task")


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("task")


class CustomLoginView(LoginView):
    template_name = "todo/login.html"
    fields = "__all__"
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse_lazy("task")


class RegisterPage(FormView):
    template_name = "todo/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("task")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("task")
        return super(RegisterPage, self).get(*args, **kwargs)
    