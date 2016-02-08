from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django.contrib.auth.models import User

from apps.curia_vista.models import AffairVote


class Organisation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='organisation_logo')

    def __str__(self):
        return self.user.get_full_name()


class RankedAffairVote(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    affair_vote = models.ForeignKey(AffairVote, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: '{}'".format(self.organisation.user.first_name, self.affair_vote.affair.title)


class AffairVoteKarma(models.Model):
    ranked_affair_vote = models.ForeignKey(RankedAffairVote, on_delete=models.CASCADE)
    karma = models.IntegerField(validators=[MinValueValidator(-3), MaxValueValidator(3)], default=0)
    vote_decision = models.CharField(max_length=255)

    class Meta:
        unique_together = ('ranked_affair_vote', 'vote_decision')

    def __str__(self):
        return "{}: {}".format(self.vote_decision, self.karma)
