from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import re_path, reverse
from django.utils.html import format_html

from .forms import (
    RequestProblemForm,
    ReturnProblemForm,
    SetGradeForm,
    ChangeScore,
    RequestForDuelForm,
    SetDuelWinner
)
from .models import *


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'score', 'current_duels_count', 'solved_problems', 'team_actions', )
    readonly_fields = (
        'id',
        'team_actions'
    )

    ordering = ('name', )

    search_fields = ('name', )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<team_id>.+)/solve-attempt/$',
                self.admin_site.admin_view(self.process_solve_attempt),
                name='solve-attempt',
            ),
            re_path(
                r'^(?P<team_id>.+)/return-problem/$',
                self.admin_site.admin_view(self.process_return_problem),
                name='return-problem',
            ),
            re_path(
                r'^(?P<team_id>.+)/set-grade/$',
                self.admin_site.admin_view(self.process_set_grade),
                name='set-grade',
            ),
            re_path(
                r'^(?P<team_id>.+)/modify-score/$',
                self.admin_site.admin_view(self.process_modify_score),
                name='modify-score',
            ),
            re_path(
                r'^(?P<team_id>.+)/request-duel/$',
                self.admin_site.admin_view(self.process_request_duel),
                name='request-duel',
            ),
        ]
        return custom_urls + urls

    def team_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">request problem</a>&nbsp;'
            '<a class="button" href="{}">modify score</a>&nbsp;'
            '<a class="button" href="{}">set grade</a>&nbsp;'
            '<a class="button" href="{}">return problem</a>&nbsp;'
            '<a class="button" href="{}">request duel</a>&nbsp;',
            reverse('admin:solve-attempt', args=[obj.pk]),
            reverse('admin:modify-score', args=[obj.pk]),
            reverse('admin:set-grade', args=[obj.pk]),
            reverse('admin:return-problem', args=[obj.pk]),
            reverse('admin:request-duel', args=[obj.pk]),
        )
    team_actions.short_description = 'Team Actions'
    team_actions.allow_tags = True

    def process_request_duel(self, request, team_id, *args, **kwargs):
        return self.process_action(
            request=request,
            team_id=team_id,
            action_form=RequestForDuelForm,
            action_title='Request For Duel'
        )

    def process_modify_score(self, request, team_id, *args, **kwargs):
        return self.process_action(
            request=request,
            team_id=team_id,
            action_form=ChangeScore,
            action_title='Change Team Score'
        )

    def process_set_grade(self, request, team_id, *args, **kwargs):
        return self.process_action(
            request=request,
            team_id=team_id,
            action_form=SetGradeForm,
            action_title='Return Problem'
        )

    def process_return_problem(self, request, team_id, *args, **kwargs):
        return self.process_action(
            request=request,
            team_id=team_id,
            action_form=ReturnProblemForm,
            action_title='Return Problem'
        )

    def process_solve_attempt(self, request, team_id, *args, **kwargs):
        return self.process_action(
            request=request,
            team_id=team_id,
            action_form=RequestProblemForm,
            action_title='Request Problem',
        )

    def process_action(self, request,
                       team_id,
                       action_form,
                       action_title):

        team = self.get_object(request, team_id)

        if request.method == 'POST':
            form = action_form(request.POST, team_id=team_id)
            if form.is_valid():
                try:
                    form.save()
                except Exception as e:
                    self.message_user(request, f'sth went wrong: {str(e)}', level=messages.ERROR)
                else:
                    self.message_user(request, 'Success')
                    url = reverse(
                        'admin:contest_team_changelist',
                        # args=[team_id],
                        current_app=self.admin_site.name,
                    )
                    return HttpResponseRedirect(url)
            else:
                self.message_user(request, f"sth went wrong: {form.errors}", level=messages.ERROR)
                context = self.admin_site.each_context(request)
                context['opts'] = self.model._meta
                context['form'] = form
                context['team'] = team
                context['title'] = action_title

                return TemplateResponse(
                    request,
                    'admin/team/team_action.html',
                    context,
                )

        form = action_form(team_id=team_id)
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['team'] = team
        context['title'] = action_title

        return TemplateResponse(
            request,
            'admin/team/team_action.html',
            context,
        )


# class SolvingAttemptForm(forms.ModelForm):
#     purchase_from = forms.ModelChoiceField(queryset=SolvingAttempt.objects.filter(problem=))
#

# @admin.register(SolvingAttempt)
# class SolvingAttemptAdmin(admin.ModelAdmin):
#     readonly_fields = ('is_purchased', 'get_duration')
#     list_display = ('id', 'team_id', 'problem', 'state', 'grade', 'get_duration',
#                     'purchased_from', 'purchased_timedelta', 'purchased_grade', 'purchase_cost')
#     list_filter = ('team', 'problem', 'state')


@admin.register(Duel)
class DuelAdmin(admin.ModelAdmin):
    list_display = ('id', 'requested_by', 'req_returned',
                    'to', 'to_returned', 'problem', 'pending', 'type', 'winner', 'duel_actions')
    list_filter = ('requested_by', 'to', 'pending')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<duel_id>.+)/set-winner/$',
                self.admin_site.admin_view(self.process_set_winner),
                name='set-winner',
            ),
        ]
        return custom_urls + urls
    
    def duel_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">set winner</a>&nbsp;',
            reverse('admin:set-winner', args=[obj.pk]),
        )
    duel_actions.short_description = 'Duel Actions'
    duel_actions.allow_tags = True

    def process_set_winner(self, request, duel_id, *args, **kwargs):
        return self.process_action(
            request=request,
            duel_id=duel_id,
            action_form=SetDuelWinner,
            action_title='Set Duel Winner'
        )

    def process_action(self, request,
                       duel_id,
                       action_form,
                       action_title):

        duel = self.get_object(request, duel_id)

        if request.method == 'POST':
            form = action_form(request.POST, duel=duel)
            if form.is_valid():
                try:
                    form.save()
                except Exception as e:
                    self.message_user(request, f'sth went wrong: {str(e)}', level=messages.ERROR)
                else:
                    self.message_user(request, 'Success')
                    url = reverse(
                        'admin:contest_duel_changelist',
                        current_app=self.admin_site.name,
                    )
                    return HttpResponseRedirect(url)
            context = self.admin_site.each_context(request)
            context['opts'] = self.model._meta
            context['form'] = form
            context['title'] = action_title

            return TemplateResponse(
                request,
                'admin/team/team_action.html',
                context,
            )

        form = action_form(duel=duel)
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['title'] = action_title

        return TemplateResponse(
            request,
            'admin/team/team_action.html',
            context,
        )


@admin.register(Transaction)
class DuelAdmin(admin.ModelAdmin):
    list_display = ('decreased_from', 'increased_to', 'amount', 'reason', 'extra')

    search_fields = ('decreased_from__name', 'increased_to__name')

    list_filter = ('reason', 'decreased_from', 'increased_to')


admin.site.register(Problem)
