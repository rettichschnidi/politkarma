from modeltranslation.translator import register, TranslationOptions

from apps.curia_vista.models import *


@register(Council)
class CouncilTranslationOptions(TranslationOptions):
    fields = ('name', 'abbreviation')


@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('name', 'abbreviation')


@register(Canton)
class CantonTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(LegislativePeriod)
class LegislativePeriodTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(AffairSummary)
class AffairSummaryTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Faction)
class FactionTranslationOptions(TranslationOptions):
    fields = ('name', 'short_name')


@register(Session)
class SessionTranslationOptions(TranslationOptions):
    fields = ('name',)
