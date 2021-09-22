from django.db import models
from django.urls import reverse


class Analysis(models.Model):
	file = models.FileField(null=False, blank=False)

	def get_absolute_url(self):
		return reverse('analysis:detail', kwargs={'id': self.id})

	def get_create_url(self):
#		return reverse('analysis:create')
		return reverse('home')

	def get_from_results(self):
		return reverse('analysis:detail2', kwargs={'id': self.id})



	class Meta:
		ordering = ['-id']

