# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.

class MP(models.Model):
    name = models.CharField('Nome completo', max_length=300)
    shortname = models.CharField('Nome abreviado', max_length=200)
    dob = models.DateField('Data de nascimento', blank=True, null=True)
    occupation = models.CharField('Profissão', max_length=300, blank=True)

    def __unicode__(self): return self.shortname
    class Meta:
        verbose_name = 'deputado'

class Party(models.Model):
    name = models.CharField('Nome', max_length=100, blank=True)
    abbrev = models.CharField('Sigla', max_length=20)

    def __unicode__(self): return self.abbrev
    class Meta:
        verbose_name = 'partido'

class FactType(models.Model):
    name = models.CharField('Nome', max_length=100)

    def __unicode__(self): return self.name
    class Meta:
        verbose_name = 'tipo de facto'
        verbose_name_plural = 'tipos de facto'

class Fact(models.Model):
    mp = models.ForeignKey(MP)
    fact_type = models.ForeignKey(FactType)
    value = models.TextField('Valor', max_length=2000)

    def __unicode__(self): return "%s - %s" % (self.fact_type.name, self.value)
    class Meta:
        verbose_name = 'facto'

class Caucus(models.Model):
    mp = models.ForeignKey(MP)
    session = models.CharField('Sessão legislativa', max_length=100)
    date_begin = models.DateField('Data início', blank=True, null=True)
    date_end = models.DateField('Data fim', blank=True, null=True)
    constituency = models.CharField('Círculo eleitoral', max_length=100)
    party = models.ForeignKey(Party)
    has_activity = models.BooleanField('Tem actividades?')
    has_registointeresses = models.BooleanField('Tem registo de interesses?')

    def __unicode__(self): return self.mp.shortname
    class Meta:
        verbose_name = 'círculo eleitoral'
        verbose_name_plural = 'círculos eleitorais'

class Activity(models.Model):
    mp = models.ForeignKey(MP)
    caucus = models.ForeignKey(Caucus)
    type1 = models.CharField('Tipo 1', max_length=50, blank=True)
    type2 = models.CharField('Tipo 2', max_length=50, blank=True)
    number = models.CharField('Número', max_length=50, blank=True)
    session = models.PositiveIntegerField('Sessão', blank=True)
    content = models.TextField('Conteúdo', max_length=3000)
    external_id = models.IntegerField('ID Externo')

    def __unicode__(self): return self.mp.shortname
    class Meta:
        verbose_name = 'actividade'