from django.db import models

# Create your models here.
class LabReport(models.Model):

    title = models.CharField(max_length=255)
    experiment_id = models.CharField(max_length=12, default='chdl-[1234]', verbose_name='ID')
    description = models.CharField(max_length=255)
    methods_intro = models.TextField(default='Enter a long description of the experiment', verbose_name='-verbose')
    methods = models.TextField()
    query = models.TextField()
    conclusion_1 = models.TextField(verbose_name='what we learned')
    conclusion_2 = models.TextField(verbose_name='further investigation')

    class Meta:
        db_table = 'labReports'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('labReport_detail', kwargs={'pk': self.pk})
