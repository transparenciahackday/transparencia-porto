#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.utils.safestring import mark_safe

from deputados.models import MP

entry_choices = [
        ('mp', 1),
        ('president', 2),
        ('statement', 3),
        ('interruption', 4),
        ('applause', 5),
        ('protest', 6),
        ('laughter', 7),
        ('note', 8),
        ('other', 9)
        ]

ENTRY_TYPES = dict((k,v) for (k,v) in entry_choices)


class Day(models.Model):
    date = models.DateField()
    def __unicode__(self):
        return str(self.date)

class Entry(models.Model):
    day = models.ForeignKey(Day)
    mp = models.ForeignKey(MP, blank=True, null=True)
    speaker = models.CharField('Orador', max_length=200)
    party = models.CharField('Partido', max_length=200, blank=True)
    text = models.TextField('Texto', max_length=10000)
    type = models.PositiveIntegerField('Tipo de intervenção', choices=entry_choices, blank=True, null=True)

    def text_as_html(self):
        paras = self.text.split('\\n')
        output = ''
        for para in paras:
            output += '<p>%s</p> ' % para 
        return mark_safe(output)

    @property
    def is_applause(self):
        if self.type == ENTRY_TYPES['applause']:
            return True
        return False

    @property
    def is_protest(self):
        if self.type == ENTRY_TYPES['protest']:
            return True
        return False

    @property
    def is_laughter(self):
        if self.type == ENTRY_TYPES['laughter']:
            return True
        return False

    @property
    def is_interruption(self):
        if self.type == ENTRY_TYPES['interruption']:
            return True
        #if self.is_protest or self.is_applause:
        #    return False
        if 'Muito bem!' in self.text:
            return True
        # see if it's a short intervention
        #if len(self.text.split(' ')) < 10:
        #    return True
        return False

    @property
    def is_regular(self):
        if self.is_applause or self.is_protest or self.is_interruption or self.is_laughter:
            return False
        return True


