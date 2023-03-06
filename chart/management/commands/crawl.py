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

            # AHCの自動更新
            for contest in ahc_list:
                if contest['auto_update'] == True or options['all']:
                    contest_screen_name = contest['contest_screen_name']
                    standing_json = info.get_standings_json(
                        contest_screen_name)
                    info.update_chart_info(
                        contest_screen_name, None, standing_json)

            # 次のAHCがあれば取得する
            latest_contest_screen_name = ahc_list[-1]['contest_screen_name']
            next_contest_screen_name = 'ahc' + \
                str(int(latest_contest_screen_name[3:6])+1).zfill(3)
            next_contest_standings_json = info.get_standings_json(
                next_contest_screen_name)

            while True:
                if (next_contest_standings_json == None):
                    break
                info.update_chart_info(
                    next_contest_screen_name, None, next_contest_standings_json)

                ahc_list.append({
                    'contest_screen_name': next_contest_screen_name,
                    'auto_update': True
                })

                next_contest_screen_name = 'ahc' + \
                    str(int(next_contest_screen_name[3:6])+1).zfill(3)
                next_contest_standings_json = info.get_standings_json(
                    next_contest_screen_name)

        number_of_contests = len(ahc_list)
        for i in range(0, number_of_contests-3):
            ahc_list[i]['auto_update'] = False
        for i in range(number_of_contests-1, max(0, number_of_contests-4), -1):
            ahc_list[i]['auto_update'] = True

        with open(BASE_DIR / 'ahc.json', 'w') as f:
            json.dump(ahc_list, f)

        # その他のコンテストの更新
        with open(BASE_DIR / 'others.json', 'r') as f:
            other_contests_list = json.load(f)

            for contest in other_contests_list:
                if contest['auto_update_all'] == True:
                    contest_screen_name = contest['contest_screen_name']
                    standing_json = info.get_standings_json(
                        contest_screen_name)
                    info.update_chart_info(
                        contest_screen_name, None, standing_json)

            # タスクごとに更新（todo）

        return
