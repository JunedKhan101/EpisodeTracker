from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Series, Seasons
from django.conf import settings

class DateInput(forms.DateInput):
	input_type = 'date'

class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, help_text="30 characters or fewer. Letters, digits and @/./+/-/_ only.")
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=254, help_text='Required.')
    birth_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, required=False, widget=DateInput, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'birth_date', 'first_name', 'last_name', 'email', 'password1', 'password2', )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class EditProfileForm(UserChangeForm):
	username = forms.CharField(max_length=30, required=True, help_text="30 characters or fewer. Letters, digits and @/./+/-/_ only.")
	birth_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, required=False, widget=DateInput,)
	email = forms.EmailField(max_length=254, required=True,)
	password = None
	class Meta:
		model = User
		fields = ('username', 'birth_date', 'first_name', 'last_name', 'email',)

	def __init__(self, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'

class SeriesForm(forms.ModelForm):
	class Meta:
		model = Series
		fields = ('SeriesName', 'is_multiple_seasons', 'NoEpisodes', 'EpisodesWatched', 'Label', 'CoverImage',)
		labels = {
			"SeriesName": "Series Name:",
			"is_multiple_seasons": "My series contains multiple seasons ",
			"NoEpisodes": "Number of episodes:",
			"EpisodesWatched": "Episodes watched:",
			"Label": "Label:",
			"CoverImage": "Add a cover image:",
		}

	def __init__(self, *args, **kwargs):
		super(SeriesForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			if visible.field.widget.input_type == 'file':
				visible.field.widget.attrs['class'] = 'form-control-file'
				continue
			visible.field.widget.attrs['class'] = 'form-control'

	def clean(self):
		# cleaned_data = super().clean()
		# print(cleaned_data) # to see all fields in console
		# episodes = cleaned_data.get('NoEpisodes')
		# episodeswatched = cleaned_data.get('EpisodesWatched')
		
		if self.cleaned_data['is_multiple_seasons'] is True:
			self.cleaned_data['NoEpisodes'] = 0
			self.cleaned_data['EpisodesWatched'] = 0
		else:
			episodes = self.cleaned_data['NoEpisodes']
			episodeswatched = self.cleaned_data['EpisodesWatched']
			if episodeswatched is None:
				episodeswatched = 0
			# print(episodes)
			# print(episodeswatched)
			if episodeswatched > episodes or episodes < episodeswatched:
				raise forms.ValidationError('Error creating series, Episodes watched can\'t be greater than number of episodes')

class SeasonsForm(forms.ModelForm):
	class Meta:
		model = Seasons
		fields = ('SeasonName', 'NoEpisodes', 'EpisodesWatched',)
		labels = {
			"SeasonName": "Season Name:",
			"NoEpisodes": "Number of episodes:",
			"EpisodesWatched": "Episodes watched:",
		}

	def __init__(self, *args, **kwargs):
		super(SeasonsForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'

	def clean(self):
		episodes = self.cleaned_data['NoEpisodes']
		episodeswatched = self.cleaned_data['EpisodesWatched']
		if episodeswatched is None:
			episodeswatched = 0
		if episodeswatched > episodes or episodes < episodeswatched:
			raise forms.ValidationError('Error creating series, Episodes watched can\'t be greater than number of episodes')