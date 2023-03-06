import json
from datetime import datetime, timezone

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .forms import InputForm
from .models import ContestInfo, ResultInfo, TaskInfo


class IndexView(View):
    form_class = InputForm
    template_name = 'chart/index.html'

    def get(self, request, *args, **kwargs):
        # フォーム描画
        form = self.form_class()

        if not 'contest' in request.GET:
            return render(request, self.template_name, {
                'form': form,
            })

        contest_screen_name = request.GET['contest']
        standings_info = {}

        # コンテスト情報取得
        try:
            contest = ContestInfo.objects.get(screen_name=contest_screen_name)

        except ContestInfo.DoesNotExist:
            return render(request, self.template_name, {
                'form': form,
                'invalid_contest': True
            })

        form = self.form_class({
            'contest': contest_screen_name
        })

        standings_info['contest_info'] = {
            'screen_name': contest_screen_name,
            'name': contest.name,
            'start_time': contest.start_time.isoformat(),
            'finish_time': contest.finish_time.isoformat()
        }

        # タスク，リザルト情報取得
        standings_info['task_info'] = {}
        contest_pk = contest.pk
        tasks = TaskInfo.objects.filter(contest__pk=contest_pk)
        for task in tasks:
            results = ResultInfo.objects.filter(task__pk=task.pk)
            result_info = {}

            for result in results:
                result_info[result.user_name] = {
                    'score': result.score
                }

            task_name = ''
            if datetime.now(timezone.utc) > contest.finish_time:
                task_name = task.name

            standings_info['task_info'][task.screen_name] = {
                'update_time': task.update_time.isoformat(),
                'assignment' : task.assignment,
                'name': task_name,
                'result_info': result_info,
            }

        if 'data' in request.GET:
            return HttpResponse(json.dumps(standings_info))

        return render(request, self.template_name, {
            'form': form,
            'standings_info': standings_info
        })
