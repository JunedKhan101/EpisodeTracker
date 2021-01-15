from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from EpisodeTracker.forms import SignUpForm, EditProfileForm, SeriesForm, SeasonsForm
from django.core.mail import send_mail
from .models import Series
from django.shortcuts import get_object_or_404

def homeview(request):
	return render(request, "index.html", {})

def signupview(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def profileview(request):
    if not request.user.is_anonymous:
        form = EditProfileForm(instance=request.user)
    if request.user.is_anonymous:
        return render(request, "profile.html")
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.save()
            messages.success(request, "Changes saved successfully")
            return HttpResponseRedirect('/profile/')
        else:
            form = EditProfileForm(instance=request.user)
            messages.error(request, "Something went wrong, maybe the username your're tying to add is already taken.")
            return HttpResponseRedirect('/profile/')
    return render(request, "profile.html", {'form': form})

def changepwd(request):
    form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            update_session_auth_hash(request, user)  # Important!
            send_mail(
            'Password changed', 'Hi ' + user.username + ', your password has been successfully changed. If you didn\'t did this then you might consider taking some action', None, [user.email], fail_silently=True)
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'changepwd.html', {'form': form})

def seriesview(request):
    form = SeriesForm(request.POST or None)
    obj = Series.objects.filter(user_id=request.user.id)

    if request.session.get('layout', None) != '/series':
        request.session['layout'] = '/series'

    if request.method == 'POST':
        form = SeriesForm(request.POST, request.FILES)
        if form.is_valid():
            episodeswatched = form.cleaned_data['EpisodesWatched']
            if episodeswatched == None:
                messages.error(request, "Episodes Watched can't be empty. Enter 0 if you haven't watched any episodes")
                return HttpResponseRedirect('/series/')
            instance = form.save()
            instance.user = request.user
            instance.save()
            return HttpResponseRedirect('/series/')
    return render(request, 'series.html', {'form': form, 'obj': obj})

def serieslistview(request):
    form = SeriesForm(request.POST or None)
    obj = Series.objects.filter(user_id=request.user.id)

    if request.session.get('layout', None) != '/series/list':
        request.session['layout'] = '/series/list'

    if request.method == 'POST':
        form = SeriesForm(request.POST, request.FILES)
        if form.is_valid():
            episodeswatched = form.cleaned_data['EpisodesWatched']
            if episodeswatched == None:
                messages.error(request, "Episodes Watched can't be empty. Enter 0 if you haven't watched any episodes")
                return HttpResponseRedirect('/series/list')
            instance = form.save()
            instance.user = request.user
            instance.save()
            return HttpResponseRedirect('/series/list')
    return render(request, 'serieslist.html', {'form': form, 'obj': obj})

def seriessimpleview(request):
    form = SeriesForm(request.POST or None)
    obj = Series.objects.filter(user_id=request.user.id)

    if request.session.get('layout', None) != '/series/simple':
        request.session['layout'] = '/series/simple'

    if request.method == 'POST':
        form = SeriesForm(request.POST, request.FILES)
        if form.is_valid():
            episodeswatched = form.cleaned_data['EpisodesWatched']
            if episodeswatched == None:
                messages.error(request, "Episodes Watched can't be empty. Enter 0 if you haven't watched any episodes")
                return HttpResponseRedirect('/series/simple')
            instance = form.save()
            instance.user = request.user
            instance.save()
            return HttpResponseRedirect('/series/simple')
    return render(request, 'seriessimple.html', {'form': form, 'obj': obj})

def aboutview(request):
    return render(request, 'about.html', {})

def reportview(request):
    if request.method == 'POST':
        subject = request.POST['title']
        body = request.POST['description']
        send_mail(subject, body, None, ['k.sonuc101@gmail.com'], fail_silently=True)
    return render(request, 'report.html', {})

def notfoundview(request):
    return render(request, 'notfound.html', {})

def seriespage(request, slug):
    series = Series.objects.filter(slug=slug)
    series = series[0]
    seasons = series.seasons_set.all()

    TotalEpisodes = 0
    TotalEpisodesWatched = 0
    if series.is_multiple_seasons == True:
        for i in seasons:
            TotalEpisodes += i.SeasonNoEpisodes
            TotalEpisodesWatched += i.SeasonEpisodesWatched
    else:
        TotalEpisodes = series.NoEpisodes
        TotalEpisodesWatched = series.EpisodesWatched

    try:
        progress_percentage = round((TotalEpisodesWatched / TotalEpisodes) * 100);
    except ZeroDivisionError:
        progress_percentage = 0

    seasonform = SeasonsForm(request.POST or None)
    seriesform = SeriesForm(request.POST or None)
    series = get_object_or_404(Series, pk = series.pk)

    if request.method == 'POST':
        if 'season' in request.POST:
            print('Inside season view')
            seasonform = SeasonsForm(request.POST)
            if seasonform.is_valid():
                episodeswatched = seasonform.cleaned_data['SeasonEpisodesWatched']
                if episodeswatched == None:
                    messages.error(request, "Episodes Watched can't be empty. Enter 0 if you haven't watched any episodes", extra_tags='season')
                    return HttpResponseRedirect('/series/%s' % slug)
                instance = seasonform.save(commit=False)
                instance.Series = series
                instance.save()
                return HttpResponseRedirect('/series/%s' % slug)
                
        elif 'series' in request.POST:
            print('Inside series view')
            seriesform = SeriesForm(request.POST, request.FILES, instance=series)
            if seriesform.is_valid():
                episodeswatched = seriesform.cleaned_data['EpisodesWatched']
                if episodeswatched == None:
                    messages.error(request, "Episodes Watched can't be empty. Enter 0 if you haven't watched any episodes", extra_tags='series')
                    return HttpResponseRedirect('/series/')
                instance = seriesform.save()
                instance.user = request.user
                instance.save()
                return HttpResponseRedirect('/series/%s' % slug)
    else:
        seasonform = SeasonsForm()
        seriesform = SeriesForm(instance=series)

    data =  {
    'seasonform': seasonform, 
    'seriesform': seriesform,
    'slug': slug, 
    'series': series, 
    'seasons': seasons,
    'percent': progress_percentage,
    }
    return render(request, 'seriespage.html', data)

def seasonspage(request, series_slug, season_slug):
    series = Series.objects.filter(slug = series_slug)
    series = series[0]
    seasons = series.seasons_set.filter(slug=season_slug)
    season = seasons[0]
    return render(request, 'seasons.html', {'series': series, 'season': season})