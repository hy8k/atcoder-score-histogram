from django import forms

from .models import ContestInfo
import time


def create_choices():
    contests = ContestInfo.objects.order_by('start_time').reverse()
    choices = []
    now_time = time.time()
    for c in contests:
        if c.start_time.timestamp() < now_time+300:
            choices.append((c.screen_name, c.name))
    return choices


class InputForm(forms.Form):
    contest = forms.ChoiceField(choices=create_choices())
