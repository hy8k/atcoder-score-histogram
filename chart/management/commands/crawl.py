import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

import chart.info as info

BASE_DIR = Path(__file__).resolve().parent.parent.parent / 'contest'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-a', '--all', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        with open(BASE_DIR / 'ahc.json', 'r') as f:
            ahc_list = json.load(f)
            contests = ahc_list['contests']

            # AHCの自動更新
            for contest in contests:
                if contest['auto_update'] == True or options['all']:
                    contest_screen_name = contest['contest_screen_name']
                    standings_json = info.get_standings_json(
                        contest_screen_name)
                    info.update_chart_info(
                        contest_screen_name, None, standings_json)

            # 次のAHCがあれば取得する
            latest_contest_screen_name = contests[-1]['contest_screen_name']
            next_contest_screen_name = 'ahc' + \
                str(int(latest_contest_screen_name[3:6])+1).zfill(3)
            next_contest_standings_json = info.get_standings_json(
                next_contest_screen_name)

            while True:
                if (next_contest_standings_json == None):
                    break
                info.update_chart_info(
                    next_contest_screen_name, None, next_contest_standings_json)

                contests.append({
                    'contest_screen_name': next_contest_screen_name,
                    'auto_update': True
                })

                next_contest_screen_name = 'ahc' + \
                    str(int(next_contest_screen_name[3:6])+1).zfill(3)
                next_contest_standings_json = info.get_standings_json(
                    next_contest_screen_name)

        # 次回の自動更新に係る処理
        # auto: 最新3件以外は自動更新しない
        # semi-auto: 最新3件以外の自動更新を許容する（auto_updateを手動で設定可能）
        if ahc_list['update_mode'] == 'auto':
            number_of_contests = len(contests)
            for i in range(0, number_of_contests-3):
                contests[i]['auto_update'] = False
            for i in range(number_of_contests-1, max(0, number_of_contests-4), -1):
                contests[i]['auto_update'] = True

        ahc_list['contests'] = contests
        with open(BASE_DIR / 'ahc.json', 'w') as f:
            json.dump(ahc_list, f)

        # その他のコンテストの更新
        with open(BASE_DIR / 'others.json', 'r') as f:
            other_contests_list = json.load(f)

            for contest in other_contests_list:
                contest_screen_name = contest['contest_screen_name']
                standings_json = info.get_standings_json(contest_screen_name)

                if contest['auto_update_all'] == True:
                    info.update_chart_info(
                        contest_screen_name, None, standings_json)
                elif contest['tasks'] != []:
                    task_list = set()
                    for task in contest['tasks']:
                        if task['auto_update'] == True:
                            task_list.add(task['screen_name'])

                    info.update_chart_info(
                        contest_screen_name, task_list, standings_json)
