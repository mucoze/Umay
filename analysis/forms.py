from django import forms
from .models import Analysis

class AnalysisForm(forms.ModelForm):

	class Meta:
		model = Analysis
		fields = [
			'file',
		]
