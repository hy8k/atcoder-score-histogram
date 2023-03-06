from django.core.management.base import BaseCommand
from django.db import transaction

import chart.info as info


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('contest_screen_name', type=str)
        parser.add_argument('-t', '--task_screen_names', type=str, nargs='*')

    @transaction.atomic
    def handle(self, *args, **options):
        contest_screen_name = options['contest_screen_name']
        task_screen_names = options['task_screen_names']

        standings_json = info.get_standings_json(contest_screen_name)
        if standings_json == None:
            raise Exception('Standings does not exist.')
        info.update_chart_info(contest_screen_name,
                               task_screen_names, standings_json)
        return
