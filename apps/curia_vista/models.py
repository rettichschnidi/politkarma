from django.db import models
from django.utils.translation import ugettext as _


# 4.1 Councils
class Council(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=2)
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=1, unique=True)

    def __str__(self):
        return _(self.name)


# 4.2 Council members
class Councillor(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    active = models.BooleanField()
    code = models.CharField(null=True, max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    number = models.IntegerField(null=True)
    official_denomination = models.CharField(null=True, max_length=255)
    salutation_letter = models.CharField(null=True, max_length=255)
    salutation_title = models.CharField(null=True, max_length=255)

    def __str__(self):
        return _("{} {}".format(self.last_name, self.first_name))


# 4.3 Schedules
class Schedule(models.Model):
    pass


# 4.4 Items of business
class Affair(models.Model):
    pass


# 4.5 Summaries
class AffairSummarie(models.Model):
    pass


# 4.6 Committees
class Committee(models.Model):
    pass


# 4.7 Legislative periods
class LegislativePeriod(models.Model):
    pass


# 4.8 Departments
class Department(models.Model):
    pass


# 4.9 Cantons
class Canton(models.Model):
    pass


# 4.10 Parliamentary groups
class Faction(models.Model):
    pass


# 4.11 Sessions
class Session(models.Model):
    pass


# 4.12 Parties
class Party(models.Model):
    pass


# 4.13 Votes
class Vote(models.Model):
    pass
