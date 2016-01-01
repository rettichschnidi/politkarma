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
