from django.db import models


# 4.1 Councils
# HTML: http://ws.parlament.ch/councils
# Data: http://ws.parlament.ch/councils?format=xml
# XSD: http://ws.parlament.ch/councils?format=xsd
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
# HTML: http://ws.parlament.ch/councillors
# Data: http://ws.parlament.ch/councillors?format=xml
# XSD: http://ws.parlament.ch/councillors?format=xsd
#
# TODO: Extend model and import:
#  - http://ws.parlament.ch/councillors/basicdetails
#  - http://ws.parlament.ch/councillors/historic
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
# HTML: http://ws.parlament.ch/schedules
# Data: http://ws.parlament.ch/schedules?format=xml
# XSD: http://ws.parlament.ch/schedules?format=xsd
#
# TODO: Extend model and import: http://ws.parlament.ch/schedules/<Jahr>/ALL
class Schedule(models.Model):
    int = models.IntegerField()


# 4.4 Items of business
# HTML: http://ws.parlament.ch/affairs
# Data: http://ws.parlament.ch/affairs?format=xml
# XSD: http://ws.parlament.ch/affairs?format=xsd
#
# TODO: Extend model and import: http://ws.parlament.ch/affairs/<ID>
class Affair(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    short_id = models.CharField(max_length=255)

    def __str__(self):
        return self.short_id


# HTML: http://ws.parlament.ch/affairs/types
# Data: http://ws.parlament.ch/affairs/types?format=xml
# XSD: http://ws.parlament.ch/affairs/types?format=xsd
class AffairType(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# HTML: http://ws.parlament.ch/affairs/topics
# Data: http://ws.parlament.ch/affairs/topics?format=xml
# XSD: http://ws.parlament.ch/affairs/topics?format=xsd
class AffairTopic(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# HTML: http://ws.parlament.ch/affairs/states
# Data: http://ws.parlament.ch/affairs/states?format=xml
# XSD: http://ws.parlament.ch/affairs/states?format=xsd
class AffairState(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    # see http://stackoverflow.com/questions/524714/does-python-have-class-prototypes-or-forward-declarations
    parent = models.ForeignKey('AffairState', null=True, blank=True)
    sorting = models.IntegerField()

    def __str__(self):
        return self.name


# 4.5 Summaries
# HTML: http://ws.parlament.ch/affairsummaries
# Data: http://ws.parlament.ch/affairsummaries?format=xml
# XSD: http://ws.parlament.ch/affairsummaries?format=xsd
#
# TODO: Extend model and import: http://ws.parlament.ch/affairsummaries/<ID>
class AffairSummary(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    formatted_id = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)

    def __str__(self):
        return self.title


# 4.6 Committees
# HTML: http://ws.parlament.ch/committees
# Data: http://ws.parlament.ch/committees?format=xml
# XSD: http://ws.parlament.ch/committees?format=xsd
#
# TODO: Extend model and import: http://ws.parlament.ch/committees/<ID>
class Committee(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    number = models.IntegerField()
    sub_number = models.IntegerField(null=True)
    council = models.ForeignKey(to=Council)
    from_date = models.DateTimeField()
    is_active = models.BooleanField()
    name = models.CharField(max_length=255)
    to_date = models.DateTimeField(null=True)
    type_code = models.IntegerField()

    def __str__(self):
        return self.name


# 4.7 Legislative periods
# HTML: http://ws.parlament.ch/legislativeperiods
# Data: http://ws.parlament.ch/legislativeperiods?format=xml
# XSD: http://ws.parlament.ch/legislativeperiods?format=xsd
class LegislativePeriod(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.IntegerField()
    from_date = models.DateTimeField()
    name = models.CharField(unique=True, max_length=255)
    to_date = models.DateTimeField()

    def __str__(self):
        return self.name


# 4.8 Departments
# HTML: http://ws.parlament.ch/departments
# Data: http://ws.parlament.ch/departments?format=xml
# XSD: http://ws.parlament.ch/departments?format=xsd
#
# TODO: Extend model and import: http://ws.parlament.ch/departments/historic
class Department(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(unique=True, max_length=255)
    code = models.CharField(unique=True, max_length=10)
    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.abbreviation


# 4.9 Cantons
# HTML: http://ws.parlament.ch/cantons
# Data: http://ws.parlament.ch/cantons?format=xml
# XSD: http://ws.parlament.ch/cantons?format=xsd
class Canton(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(unique=True, max_length=255)
    code = models.CharField(unique=True, max_length=7)
    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.name


# 4.10 Parliamentary groups
# HTML: http://ws.parlament.ch/factions
# Data: http://ws.parlament.ch/factions?format=xml
# XSD: http://ws.parlament.ch/factions?format=xsd
#
# TODO: Can/Should we import http://ws.parlament.ch/factions/historic?
class Faction(models.Model):
    the_id = models.IntegerField()
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('the_id', 'from_date')

    def __str__(self):
        return self.name


# 4.11 Sessions
# HTML: http://ws.parlament.ch/sessions
# Data: http://ws.parlament.ch/sessions?format=xml
# XSD: http://ws.parlament.ch/sessions?format=xsd
class Session(models.Model):
    code = models.CharField(max_length=255, primary_key=True)
    updated = models.DateTimeField()
    from_date = models.DateTimeField()
    to_date = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# 4.12 Parties
# HTML: http://ws.parlament.ch/parties/historic
# Data: http://ws.parlament.ch/parties/historic?format=xml
# XSD: http://ws.parlament.ch/parties/historic?format=xsd
class Party(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# 4.13 Votes
# HTML: http://ws.parlament.ch/parties/historic
# Data: http://ws.parlament.ch/parties/historic?format=xml
# XSD: http://ws.parlament.ch/parties/historic?format=xsd
class Vote(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    title = models.CharField(max_length=255)
    affair_votes = models.IntegerField()

    def __str__(self):
        return self.title


# Affair vote, represents a single vote one on one affair. An affair can have multiple votes
# List of all affair votes:
#  HTML: http://ws.parlament.ch/votes/affairs
#  Data: http://ws.parlament.ch/votes/affairs?format=xml
#  XSD: http://ws.parlament.ch/votes/affairs?format=xsd
# Details (for example "Wirtschaftliche Vorteile dank Schengen-Partnerschaft" with id 20153896):
#  HTML: http://ws.parlament.ch/votes/affairs/20153896
#  Data: http://ws.parlament.ch/votes/affairs/20153896?format=xml
#  XSD: http://ws.parlament.ch/votes/affairs/20153896?format=xsd
#
# TODO: Do we even need this data? How about just calculating it on the fly using CouncillorVote?
class AffairVote(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    division_text = models.CharField(max_length=1024, null=True, blank=True)
    meaning_no = models.CharField(max_length=1024, null=True, blank=True)
    meaning_yes = models.CharField(max_length=1024, null=True, blank=True)
    registration_number = models.IntegerField()
    submission_text = models.CharField(max_length=1024, null=True, blank=True)
    affair = models.ForeignKey(Affair)

    def __str__(self):
        return self.division_text


# Councillor vote represents the decision of a single councillor in a AffairVote
# List of all members:
#  HTML: http://ws.parlament.ch/votes/councillors/
#  Data: http://ws.parlament.ch/votes/councillors?format=xml
#  XSD: http://ws.parlament.ch/votes/councillors?format=xsd
# Details (for example "Abate Fabio" with id 2565):
#  HTML: http://ws.parlament.ch/votes/councillors/2565
#  Data: http://ws.parlament.ch/votes/councillors/2565?format=xml
#  XSD: http://ws.parlament.ch/votes/councillors/2565?format=xsd
class CouncillorVote(models.Model):
    id = models.IntegerField(primary_key=True)
    decision = models.CharField(max_length=255)
    councillor = models.ForeignKey(Councillor)
    affair_vote = models.ForeignKey(AffairVote)

    def __str__(self):
        return self.decision


# TODO: Figure out if this model is just for caching summarized data
class AffairVoteTotal(models.Model):
    type = models.CharField(max_length=8)
    count = models.IntegerField()
    affair_vote = models.ForeignKey(AffairVote)

    class Meta:
        unique_together = ('type', 'affair_vote')

    def __str__(self):
        return "{} {}".format(self.type, self.count)


# TODO: Figure out if this model is just for caching summarized data
class FilteredAffairVoteTotal(models.Model):
    type = models.CharField(max_length=8)
    count = models.IntegerField()
    affair_vote = models.ForeignKey(AffairVote)

    class Meta:
        unique_together = ('type', 'affair_vote')

    def __str__(self):
        return "{} {}".format(self.type, self.count)
