from django.db import models
from django.utils.translation import ugettext as _


# 4.1 Councils
class Council(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=2)
    type = models.CharField(max_length=1, unique=True)

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
    title = models.CharField(max_length=1024)

    def __str__(self):
        return self.title


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
class Department(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(unique=True, max_length=255)
    code = models.CharField(unique=True, max_length=10)
    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.abbreviation


# 4.9 Cantons
class Canton(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(unique=True, max_length=255)
    code = models.CharField(unique=True, max_length=7)
    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.name


# 4.10 Parliamentary groups
class Faction(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# 4.11 Sessions
class Session(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField(null=True, blank=True)
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
