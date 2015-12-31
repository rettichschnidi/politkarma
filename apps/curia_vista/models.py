from django.db import models
from django.utils.translation import ugettext as _


# 4.1 Councils
def validate_council_code(value):
    if value not in Council.texts:
        from django.core.exceptions import ValidationError
        raise ValidationError('\'{}\' is not a valid council type'.format(value))


class Council(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=6, validators=[validate_council_code])
    # We do not want any language-specific data in the model
    # name = models.CharField(max_length=255)
    type = models.CharField(max_length=1, unique=True)

    texts = {
        'RAT_1_': ('N', _('NR'), _('Nationalrat')),
        'RAT_2_': ('S', _('SR'), _('Ständerat')),
        'RAT_3_': ('B', _('V'), _('Vereinigte Bundesversammlung')),
    }

    @property
    def name(self):
        return Council.texts[self.code][2]

    @property
    def abbreviation(self):
        return Council.texts[self.code][1]

    def __str__(self):
        return self.name


# 4.2 Council members
class Councillor(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    active = models.BooleanField()
    code = models.CharField(null=True, blank=True, max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    number = models.IntegerField(null=True, blank=True)
    official_denomination = models.CharField(null=True, blank=True, max_length=255)
    salutation_letter = models.CharField(null=True, blank=True, max_length=255)
    salutation_title = models.CharField(null=True, blank=True, max_length=255)

    @property
    def full_name(self):
        return "{} {}".format(self.last_name, self.first_name)

    def __str__(self):
        return self.full_name


# 4.3 Schedules
class Schedule(models.Model):
    int = models.IntegerField()


# 4.4 Items of business
class Affair(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    short_id = models.CharField(max_length=255)

    def __str__(self):
        return self.short_id


# 4.5 Summaries
class AffairSummary(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    formatted_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)


# 4.6 Committees
class Committee(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    committee_number = models.IntegerField()
    council = models.ForeignKey(to=Council)
    from_date = models.DateTimeField()
    is_active = models.BooleanField()
    name = models.CharField(max_length=255)
    to_date = models.DateTimeField()
    type_code = models.IntegerField()


# 4.7 Legislative periods
class LegislativePeriod(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.IntegerField()
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()

    @property
    def name(self):
        return _('{}. Legislatur'.format(self.code))

    def __str__(self):
        return self.name


# 4.8 Departments
def validate_department_code(value):
    if value not in Department.texts:
        from django.core.exceptions import ValidationError
        raise ValidationError('\'{}\' is not a valid department code'.format(value))


class Department(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(unique=True, max_length=10, validators=[validate_department_code])

    texts = {
        'DEP_1_': (_('Parl'), _('Parlament')),
        'DEP_3_': (_('EDA'), _('Departement für auswärtige Angelegenheiten')),
        'DEP_4_': (_('EDI'), _('Departement des Innern')),
        'DEP_5_': (_('EJPD'), _('Justiz- und Polizeidepartement')),
        'DEP_6_': (_('VBS'), _('Departement für Verteidigung, Bevölkerungsschutz und Sport')),
        'DEP_7_': (_('EFD'), _('Finanzdepartement')),
        'DEP_8_': (_('WBF'), _('Departement für Wirtschaft, Bildung und Forschung')),
        'DEP_9_': (_('UVEK'), _('Departement für Umwelt, Verkehr, Energie und Kommunikation')),
        'DEP_10_': (_('BK'), _('Bundeskanzlei')),
        'DEP_11_': (_('VBV'), _('Vereinigte Bundesversammlung')),
        'DEP_12_': (_('AB-BA'), _('Aufsichtsbehörde über die Bundesanwaltschaft')),
        'DEP_1482_': (_('BGer'), _('Bundesgericht'))
    }

    @property
    def name(self):
        return Department.texts[self.code][1]

    @property
    def abbreviation(self):
        return Department.texts[self.code][0]

    def __str__(self):
        return self.abbreviation


# 4.9 Cantons
def validate_canton_code(value):
    if value not in Canton.texts:
        from django.core.exceptions import ValidationError
        raise ValidationError('\'{}\' is not a valid canton code'.format(value))


class Canton(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(unique=True, max_length=7, validators=[validate_canton_code])

    texts = {
        'KAN_19_': (_('AG'), _('Aargau')),
        'KAN_15_': (_('AR'), _('Appenzell A.-Rh.')),
        'KAN_16_': (_('AI'), _('Appenzell I.-Rh.')),
        'KAN_13_': (_('BL'), _('Basel-Landschaft')),
        'KAN_12_': (_('BS'), _('Basel-Stadt')),
        'KAN_2_': (_('BE'), _('Bern')),
        'KAN_10_': (_('FR'), _('Freiburg')),
        'KAN_25_': (_('GE'), _('Genf')),
        'KAN_8_': (_('GL'), _('Glarus')),
        'KAN_18_': (_('GR'), _('Graubünden')),
        'KAN_26_': (_('Ju'), _('Jura')),
        'KAN_3_': (_('LU'), _('Luzern')),
        'KAN_24_': (_('NE'), _('Neuenburg')),
        'KAN_7_': (_('NW'), _('Nidwalden')),
        'KAN_6_': (_('OW'), _('Obwalden')),
        'KAN_14_': (_('SH'), _('Schaffhausen')),
        'KAN_5_': (_('SZ'), _('Schwyz')),
        'KAN_11_': (_('SO'), _('Solothurn')),
        'KAN_17_': (_('SG'), _('St. Gallen')),
        'KAN_27_': (_('TI'), _('Tessin')),
        'KAN_20_': (_('TG'), _('Thurgau')),
        'KAN_4_': (_('UR'), _('Uri')),
        'KAN_22_': (_('VD'), _('Waadt')),
        'KAN_23_': (_('VS'), _('Wallis')),
        'KAN_9_': (_('ZG'), _('Zug')),
        'KAN_1_': (_('ZH'), _('Zürich')),
    }

    @property
    def name(self):
        return Canton.texts[self.code][1]

    @property
    def abbreviation(self):
        return Canton.texts[self.code][0]

    def __str__(self):
        return self.name


# 4.10 Parliamentary groups
class Faction(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)


# 4.11 Sessions
class Session(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    name = models.CharField(max_length=255)


# 4.12 Parties
class Party(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)


# 4.13 Votes
class Vote(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    title = models.CharField(max_length=255)
    affair_votes = models.IntegerField()
