from django.db import models

class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)
	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value':self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)

class TermFields(models.Model):
	term = models.CharField(max_length = 50)
	weight = models.DecimalField(decimal_places = 2, max_digits=5)
	def __unicode__(self):
		return u"%s" % self.term

class TermChoices(models.Model):
	term_field = models.ForeignKey(TermFields)
	choice_label = models.CharField(max_length = 50)
	value = IntegerRangeField(min_value = 0, max_value = 5)
	def __unicode__(self):
		return u"%s" % self.term_choice