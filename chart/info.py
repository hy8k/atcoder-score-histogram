from __future__ import annotations

import json

from bs4 import BeautifulSoup
from django.utils import dateparse

from .login import login
from .models import ContestInfo, ResultInfo, TaskInfo


def get_standings_json(contest_screen_name: str):
    session = login()

    # 順位表取得
    standings_url = 'https://atcoder.jp/contests/' + \
        contest_screen_name + '/standings/json'

    r = session.get(standings_url)
    if r.status_code == 200:
        standings_json = json.loads(r.text)
        return standings_json
    else:
        return None


def get_tasks(standings_json: dict):
    return standings_json['TaskInfo']


def get_standings_data(standings_json: dict):
    return standings_json['StandingsData']


def update_chart_info(contest_screen_name: str, task_screen_names: set | None, standings_json: dict):
    tasks = get_tasks(standings_json)
    standings_data = get_standings_data(standings_json)

    print("Updating %s..." % contest_screen_name)
    update_contest_info(contest_screen_name)
    update_task_info(contest_screen_name, task_screen_names, tasks)
    update_result_info(task_screen_names, standings_data)
    return


def update_contest_info(contest_screen_name: str):
    # コンテストデータ保存
    session = login()
    contest_page_url = 'https://atcoder.jp/contests/' + contest_screen_name

    r = session.get(contest_page_url)
    if r.status_code == 200:
        contest_page = r.text
        bs = BeautifulSoup(contest_page, 'html.parser')
        name = bs.find(attrs={'class': 'contest-title'}).text

        contest_duration = bs.find_all(attrs={'class': 'fixtime-full'})
        start_time = dateparse.parse_datetime(contest_duration[0].text)
        finish_time = dateparse.parse_datetime(contest_duration[1].text)
        ContestInfo.objects.update_or_create(
            screen_name=contest_screen_name,
            name=name,
            start_time=start_time,
            finish_time=finish_time
        )
    return


def update_task_info(contest_screen_name: str, task_screen_names: set, tasks: dict):
    # タスクデータ保存

    contest_info = ContestInfo.objects.get(screen_name=contest_screen_name)
    for task in tasks:
        assignment = task['Assignment']
        screen_name = task['TaskScreenName']
        name = task['TaskName']

        if task_screen_names == None or screen_name in task_screen_names:
            TaskInfo.objects.update_or_create(
                contest=contest_info,
                assignment=assignment,
                screen_name=screen_name,
                defaults={
                    'name': name
                }
            )
    return


def update_result_info(task_screen_names: set, standings_data: dict):
    # リザルトデータ保存
    for user in standings_data:
        user_name = user['UserScreenName']
        for task_screen_name, task_result in user['TaskResults'].items():
            if task_screen_names == None or task_screen_name in task_screen_names:
                task_info = TaskInfo.objects.get(screen_name=task_screen_name)
                score = task_result['Score']
                ResultInfo.objects.update_or_create(
                    task=task_info,
                    user_name=user_name,
                    defaults={
                        'score': score
                    }
                )
    return
