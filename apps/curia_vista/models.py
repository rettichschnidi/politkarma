from django.db import models


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


class AffairType(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AffairTopic(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


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
class Session(models.Model):
    code = models.CharField(max_length=255, primary_key=True)
    updated = models.DateTimeField()
    from_date = models.DateTimeField()
    to_date = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# 4.12 Parties
class Party(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    abbreviation = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# 4.13 Votes
class Vote(models.Model):
    id = models.IntegerField(primary_key=True)
    updated = models.DateTimeField()
    title = models.CharField(max_length=255)
    affair_votes = models.IntegerField()

    def __str__(self):
        return self.title


# affair vote, represents a single vote one on one affair. An affair can have multiple votes
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
class CouncillorVote(models.Model):
    id = models.IntegerField(primary_key=True)
    decision = models.CharField(max_length=255)
    councillor = models.ForeignKey(Councillor)
    affair_vote = models.ForeignKey(AffairVote)

    def __str__(self):
        return self.decision


#
class AffairVoteTotal(models.Model):
    type = models.CharField(max_length=8)
    count = models.IntegerField()
    affair_vote = models.ForeignKey(AffairVote)

    class Meta:
        unique_together = ('type', 'affair_vote')

    def __str__(self):
        return "{} {}".format(self.type, self.count)


#
class FilteredAffairVoteTotal(models.Model):
    type = models.CharField(max_length=8)
    count = models.IntegerField()
    affair_vote = models.ForeignKey(AffairVote)

    class Meta:
        unique_together = ('type', 'affair_vote')

    def __str__(self):
        return "{} {}".format(self.type, self.count)
