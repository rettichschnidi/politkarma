from django.db import models

from django.utils.translation import ugettext_lazy as _


# 4.1 Councils
# HTML: http://ws-old.parlament.ch/councils
# Data: http://ws-old.parlament.ch/councils?format=xml
# XSD: http://ws-old.parlament.ch/councils?format=xsd
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
# Overview:
# HTML: http://ws-old.parlament.ch/councillors
# Data: http://ws-old.parlament.ch/councillors?format=xml
# XSD: http://ws-old.parlament.ch/councillors?format=xsd
class Councillor(models.Model):
    # Overview data
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

    # Basic details
    # HTML: http://ws-old.parlament.ch/councillors/basicdetails
    # Data: http://ws-old.parlament.ch/councillors/basicdetails?format=xml
    # XSD: http://ws-old.parlament.ch/councillors/basicdetails?format=xsd
    biography_url = models.URLField(blank=True, null=True)
    picture_url = models.URLField(blank=True, null=True)

    # Detailed data (for councillor with id 801):
    # HTML: http://ws-old.parlament.ch/councillors/801
    # Data: http://ws-old.parlament.ch/councillors/801?format=xml
    # XSD: http://ws-old.parlament.ch/councillors/801?format=xsd
    # TODO: Import all fields including the complex types!
    canton = models.ForeignKey('Canton', blank=True, null=True)
    council = models.ForeignKey('Council', blank=True, null=True)
    faction = models.ForeignKey('Faction', blank=True, null=True)
    homepage = models.CharField(max_length=255, blank=True, null=True)
    party = models.ForeignKey('Party', blank=True, null=True)
    birth_date = models.DateTimeField(blank=True, null=True)
    birth_canton = models.ForeignKey('Canton', blank=True, null=True, related_name=_('birth_canton'))
    birth_city = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    language = models.CharField(max_length=2, blank=True, null=True)

    @property
    def full_name(self):
        return "{} {}".format(self.last_name, self.first_name)

    def __str__(self):
        return self.full_name


# 4.3 Schedules
# HTML: http://ws-old.parlament.ch/schedules
# Data: http://ws-old.parlament.ch/schedules?format=xml
# XSD: http://ws-old.parlament.ch/schedules?format=xsd
#
# TODO: Extend model and import: http://ws-old.parlament.ch/schedules/<Jahr>/ALL
class Schedule(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    # TODO: type is http://schemas.microsoft.com/2003/10/Serialization/Arrays. not sure how to do this in django
    correspondents = models.CharField(max_length=255, blank=True, null=True)
    council = models.ForeignKey('Council')
    date = models.DateTimeField()
    date_title = models.CharField(max_length=255)
    department = models.ForeignKey('Department', blank=True, null=True)
    number = models.CharField(max_length=255)
    session = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)
    created = models.DateTimeField()


# 4.4 Items of business
# HTML: http://ws-old.parlament.ch/affairs
# Data: http://ws-old.parlament.ch/affairs?format=xml
# XSD: http://ws-old.parlament.ch/affairs?format=xsd
#
# TODO: Extend model and import: http://ws-old.parlament.ch/affairs/<ID>
class Affair(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    short_id = models.CharField(max_length=255)
    sequential_number = models.IntegerField(null=True, blank=True)
    affair_type = models.ForeignKey('AffairType', null=True, blank=True)
    author = models.ForeignKey('AffairAuthor', null=True, blank=True)
    deposit = models.ForeignKey('AffairDeposit', null=True, blank=True)
    # TODO: find an example and implement...
    descriptors = ""
    handling = models.ForeignKey('AffairHandling', null=True, blank=True)
    # de, fr or it
    language = models.CharField(null=True, blank=True, max_length=255)
    priority_councils = models.ManyToManyField('AffairPriorityCouncil')
    related_affairs = models.ManyToManyField('Affair')
    roles = models.ManyToManyField('AffairRole')
    state = models.ForeignKey('AffairState', null=True, blank=True)
    # from <state>, not part of AffairState
    done_key = models.IntegerField(null=True, blank=True)
    # from <state>, not part of AffairState
    new_key = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=1024, null=True, blank=True)
    texts = models.ManyToManyField('AffairText')

    def __str__(self):
        return self.short_id


class AffairAuthor(models.Model):
    id = models.AutoField(primary_key=True)
    councillor = models.ForeignKey('Councillor', null=True, blank=True)
    faction = models.ForeignKey('Faction', null=True, blank=True)

    def __str__(self):
        return self.id


class AffairDeposit(models.Model):
    id = models.AutoField(primary_key=True)
    council = models.ForeignKey('Council', null=True, blank=True)
    date = models.DateTimeField()
    legislative_period = models.IntegerField(null=True, blank=True)
    session = models.IntegerField()

    def __str__(self):
        return self.id


class AffairHandling(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    legislative_period = models.ForeignKey('LegislativePeriod', null=True, blank=True)
    session = models.ForeignKey('Session', null=True, blank=True)

    def __str__(self):
        return self.id


class AffairPriorityCouncil(models.Model):
    id = models.AutoField(primary_key=True)
    # TODO: remove support for null values when the issue with council 4 has been resolved
    council = models.ForeignKey('Council', null=True, blank=True)
    priority = models.IntegerField()

    def __str__(self):
        return self.id


class AffairRole(models.Model):
    id = models.AutoField(primary_key=True)
    councillor = models.ForeignKey('Councillor', null=True, blank=True)
    faction = models.ForeignKey('Faction', null=True, blank=True)
    role_type = models.CharField(max_length=255)

    def __str__(self):
        return self.id


class AffairText(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey('AffairTextType')
    value = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.id


class AffairTextType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.id


# HTML: http://ws-old.parlament.ch/affairs/types
# Data: http://ws-old.parlament.ch/affairs/types?format=xml
# XSD: http://ws-old.parlament.ch/affairs/types?format=xsd
class AffairType(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# HTML: http://ws-old.parlament.ch/affairs/topics
# Data: http://ws-old.parlament.ch/affairs/topics?format=xml
# XSD: http://ws-old.parlament.ch/affairs/topics?format=xsd
class AffairTopic(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# HTML: http://ws-old.parlament.ch/affairs/states
# Data: http://ws-old.parlament.ch/affairs/states?format=xml
# XSD: http://ws-old.parlament.ch/affairs/states?format=xsd
class AffairState(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('AffairState', null=True, blank=True)
    sorting = models.IntegerField()

    def __str__(self):
        return self.name


# 4.5 Summaries
# HTML: http://ws-old.parlament.ch/affairsummaries
# Data: http://ws-old.parlament.ch/affairsummaries?format=xml
# XSD: http://ws-old.parlament.ch/affairsummaries?format=xsd
#
# TODO: Extend model and import: http://ws-old.parlament.ch/affairsummaries/<ID>
class AffairSummary(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    formatted_id = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)

    def __str__(self):
        return self.title


# 4.6 Committees
# HTML: http://ws-old.parlament.ch/committees
# Data: http://ws-old.parlament.ch/committees?format=xml
# XSD: http://ws-old.parlament.ch/committees?format=xsd
#
# TODO: Extend model and import: http://ws-old.parlament.ch/committees/<ID>
class Committee(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    number = models.IntegerField()
    sub_number = models.IntegerField(null=True, blank=True)
    council = models.ForeignKey(Council)
    from_date = models.DateTimeField()
    is_active = models.BooleanField()
    name = models.CharField(max_length=255)
    to_date = models.DateTimeField(null=True, blank=True)
    type_code = models.IntegerField()

    def __str__(self):
        return self.name


# 4.7 Legislative periods
# HTML: http://ws-old.parlament.ch/legislativeperiods
# Data: http://ws-old.parlament.ch/legislativeperiods?format=xml
# XSD: http://ws-old.parlament.ch/legislativeperiods?format=xsd
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
# HTML: http://ws-old.parlament.ch/departments
# Data: http://ws-old.parlament.ch/departments?format=xml
# XSD: http://ws-old.parlament.ch/departments?format=xsd
#
# TODO: Extend model and import: http://ws-old.parlament.ch/departments/historic
class Department(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(unique=True, max_length=255)
    code = models.CharField(unique=True, max_length=10)
    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.abbreviation


# 4.9 Cantons
# HTML: http://ws-old.parlament.ch/cantons
# Data: http://ws-old.parlament.ch/cantons?format=xml
# XSD: http://ws-old.parlament.ch/cantons?format=xsd
class Canton(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(unique=True, max_length=255)
    code = models.CharField(unique=True, max_length=7)
    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.name


# 4.10 Parliamentary groups
# HTML: http://ws-old.parlament.ch/factions
# Data: http://ws-old.parlament.ch/factions?format=xml
# XSD: http://ws-old.parlament.ch/factions?format=xsd
#
# TODO: Can/Should we import http://ws-old.parlament.ch/factions/historic?
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
# HTML: http://ws-old.parlament.ch/sessions
# Data: http://ws-old.parlament.ch/sessions?format=xml
# XSD: http://ws-old.parlament.ch/sessions?format=xsd
class Session(models.Model):
    code = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    from_date = models.DateTimeField()
    to_date = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# 4.12 Parties
# HTML: http://ws-old.parlament.ch/parties/historic
# Data: http://ws-old.parlament.ch/parties/historic?format=xml
# XSD: http://ws-old.parlament.ch/parties/historic?format=xsd
class Party(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# 4.13 Votes
# HTML: http://ws-old.parlament.ch/parties/historic
# Data: http://ws-old.parlament.ch/parties/historic?format=xml
# XSD: http://ws-old.parlament.ch/parties/historic?format=xsd
class Vote(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    title = models.CharField(max_length=255)
    affair_votes = models.IntegerField()

    def __str__(self):
        return self.title


# Affair vote, represents a single vote one on one affair. An affair can have multiple votes
# List of all affair votes:
#  HTML: http://ws-old.parlament.ch/votes/affairs
#  Data: http://ws-old.parlament.ch/votes/affairs?format=xml
#  XSD: http://ws-old.parlament.ch/votes/affairs?format=xsd
# Details (for example "Wirtschaftliche Vorteile dank Schengen-Partnerschaft" with id 20153896):
#  HTML: http://ws-old.parlament.ch/votes/affairs/20153896
#  Data: http://ws-old.parlament.ch/votes/affairs/20153896?format=xml
#  XSD: http://ws-old.parlament.ch/votes/affairs/20153896?format=xsd
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
#  HTML: http://ws-old.parlament.ch/votes/councillors/
#  Data: http://ws-old.parlament.ch/votes/councillors?format=xml
#  XSD: http://ws-old.parlament.ch/votes/councillors?format=xsd
# Details (for example "Abate Fabio" with id 2565):
#  HTML: http://ws-old.parlament.ch/votes/councillors/2565
#  Data: http://ws-old.parlament.ch/votes/councillors/2565?format=xml
#  XSD: http://ws-old.parlament.ch/votes/councillors/2565?format=xsd
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


#
class Organization(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1024, blank=True, null=True)
    description = models.CharField(max_length=1024)
    logo_location = models.CharField(max_length=1024)

    def __str__(self):
        return self.name


#
class KarmaRule(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    organization = models.ForeignKey(Organization)
    affair_vote = models.ForeignKey(AffairVote)
    expected_decision = models.CharField(max_length=255)
    karma_multiplier = models.IntegerField()

    def __str__(self):
        return "{} {}".format(self.id, self.description)
