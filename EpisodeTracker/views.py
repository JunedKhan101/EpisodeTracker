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
                messages.error(request, "Episodes watched can't be empty. Enter 0 if you haven't watched any episodes")
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
                messages.error(request, "Episodes watched can't be empty. Enter 0 if you haven't watched any episodes")
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
                messages.error(request, "Episodes watched can't be empty. Enter 0 if you haven't watched any episodes")
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

def createList(val):
    mylist = []
    for i in range(1, val + 1):
        mylist.append(i)
    return mylist

def createUnwatchedList(episodes_watched, val):
    mylist = []
    for i in range(1, val + 1):
        mylist.append(episodes_watched + i)
    return mylist

def seriespage(request, slug):
    series = Series.objects.filter(slug=slug)
    series = series[0]
    seasons = series.seasons_set.all()

    TotalEpisodes = 0
    TotalEpisodesWatched = 0
    ListTotalEpisodes = []
    ListUnwatchedEpisodes = []
    ListTotalEpisodesWatched = []
    if series.is_multiple_seasons == True:
        for i in seasons:
            TotalEpisodes += i.SeasonNoEpisodes
            TotalEpisodesWatched += i.SeasonEpisodesWatched
    else:
        TotalEpisodes = series.NoEpisodes
        TotalEpisodesWatched = series.EpisodesWatched
        ListTotalEpisodes = createList(TotalEpisodes)
        ListTotalEpisodesWatched = createList(TotalEpisodesWatched)
        if TotalEpisodes != 0:
            ListUnwatchedEpisodes = createUnwatchedList(ListTotalEpisodesWatched[len(ListTotalEpisodesWatched) - 1], TotalEpisodes - TotalEpisodesWatched)
        else:
            ListUnwatchedEpisodes = []
    try:
        progress_percentage = round((TotalEpisodesWatched / TotalEpisodes) * 100);
    except ZeroDivisionError:
        progress_percentage = 0

    form = SeasonsForm(request.POST or None)
    series = get_object_or_404(Series, pk = series.pk)

    if request.method == 'POST':
        form = SeasonsForm(request.POST)
        if form.is_valid():
            episodeswatched = form.cleaned_data['SeasonEpisodesWatched']
            if episodeswatched == None:
                messages.error(request, "Episodes watched can't be empty. Enter 0 if you haven't watched any episodes")
                return HttpResponseRedirect('/series/%s' % slug)
            instance = form.save(commit=False)
            instance.Series = series
            instance.save()
            return HttpResponseRedirect('/series/%s' % slug)
    else:
        form = SeasonsForm()

    data =  {
        'form': form,
        'slug': slug, 
        'series': series, 
        'seasons': seasons,
        'percent': progress_percentage,
        'ListTotalEpisodes': ListTotalEpisodes,
        'ListUnwatchedEpisodes': ListUnwatchedEpisodes,
        'ListTotalEpisodesWatched': ListTotalEpisodesWatched,
    }
    return render(request, 'seriespage.html', data)

def seasonspage(request, series_slug, season_slug):
    series = Series.objects.filter(slug = series_slug)
    series = series[0]
    seasons = series.seasons_set.filter(slug=season_slug)
    season = seasons[0]

    TotalEpisodes = season.SeasonNoEpisodes
    TotalEpisodesWatched = season.SeasonEpisodesWatched
    ListTotalEpisodes = []
    ListUnwatchedEpisodes = []
    ListTotalEpisodesWatched = []

    ListTotalEpisodes = createList(TotalEpisodes)
    ListTotalEpisodesWatched = createList(TotalEpisodesWatched)
    if TotalEpisodes != 0:
        ListUnwatchedEpisodes = createUnwatchedList(ListTotalEpisodesWatched[len(ListTotalEpisodesWatched) - 1], TotalEpisodes - TotalEpisodesWatched)
    else:
        ListUnwatchedEpisodes = []

    form = SeasonsForm(request.POST or None, instance=season)
    if request.method == 'POST':
        form = SeasonsForm(request.POST, instance=season)
        if form.is_valid():
            episodeswatched = form.cleaned_data['SeasonEpisodesWatched']
            if episodeswatched == None:
                messages.error(request, "Episodes watched can't be empty. Enter 0 if you haven't watched any episodes")
                return HttpResponseRedirect('/series/%s' % slug)
            instance = form.save(commit=False)
            instance.Series = series
            instance.save()
            return HttpResponseRedirect('/series/%s/%s' % series.slug, season.slug)
    else:
        form = SeasonsForm(instance=season)

    data = {
        'form': form,
        'series': series,
        'season': season,
        'ListTotalEpisodes': ListTotalEpisodes,
        'ListUnwatchedEpisodes': ListUnwatchedEpisodes,
        'ListTotalEpisodesWatched': ListTotalEpisodesWatched,
    }
    return render(request, 'seasons.html', data)

def editseriesview(request, slug):
    series = Series.objects.filter(slug=slug)
    series = series[0]

    form = SeriesForm(request.POST or None, instance=series)
    if request.method == 'POST':
        form = SeriesForm(request.POST, request.FILES, instance=series)
        if form.is_valid():
            episodeswatched = form.cleaned_data['EpisodesWatched']
            if episodeswatched == None:
                messages.error(request, "Episodes watched can't be empty. Enter 0 if you haven't watched any episodes")
                return HttpResponseRedirect('/series/edit/%s' % slug)
            instance = form.save()
            instance.user = request.user
            instance.save()
            return HttpResponseRedirect('/series/edit/%s' % slug)
    else:
        form = SeriesForm(instance=series)
    return render(request, 'editseries.html', {'form': form,})