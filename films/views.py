from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.contrib import messages


from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods

from .models import Film, UserFilms
from films.utility import get_max_order
from films.forms import RegisterForm



class IndexView(TemplateView):
    template_name = 'index.html'
    
class Login(LoginView):
    template_name = 'registration/login.html'

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()  # save the user
        return super().form_valid(form)

class FilmList(LoginRequiredMixin ,ListView):
    template_name = 'film.html'
    paginate_by = 7
    model = Film
    context_object_name = 'films'
    
    def get_template_names(self):
        if self.request.htmx:
            return 'partials/film-list-element.html'
        else:
            return 'film.html'
    
    def get_queryset(self):
        return UserFilms.objects.prefetch_related('film').filter(user=self.request.user)
        

def check_username(request):
    username = request.POST.get('username')
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse("<div id='username-error' class='error'>This username already exists</div>")
    else:
        return HttpResponse("<div id='username-error' class='success'>This username is available</div>")
    
@login_required
def add_films(request):
    name = request.POST.get('filmname')
    film = Film.objects.get_or_create(name=name)[0]
    
    if not UserFilms.objects.filter(film=film,user=request.user).exists():
        UserFilms.objects.create(
            film=film,
            user=request.user,
            order=get_max_order(request.user)
        )
    
    films = UserFilms.objects.filter(user=request.user)
    messages.success(request,f'Added {name} to your list')
    return render(request,'partials/film-list.html',{'films':films})

@login_required
@require_http_methods(['DELETE'])
def delete_films(request,pk):
    UserFilms.objects.get(pk=pk).delete()
    films = UserFilms.objects.filter(user=request.user)
    
    return render(request,'partials/film-list.html',{'films':films})

def search_film(request):
    search_param = request.POST.get('search')
    
    user_films = UserFilms.objects.filter(user=request.user)
    results = Film.objects.filter(name__icontains=search_param).exclude(
        name__in=user_films.values_list('film__name', flat=True)
    )
    
    context = {'results':results}
    return render(request,'partials/search-result.html',context)

def clear(request):
    return HttpResponse('')

def sort(request):
    film_pks_order = request.POST.getlist('film_order')
    films = []
    updated_film = []
    userfilms = UserFilms.objects.prefetch_related('film').filter(user=request.user)
    for idx, film_pk in enumerate(film_pks_order,start=1):
        # user_film = UserFilms.objects.get(pk=film_pk)
        user_film = next(u for u in userfilms if u.pk == int(film_pk))
        if user_film.order != idx:
            user_film.order = idx
            updated_film.append(user_film)

        films.append(user_film)
    UserFilms.objects.bulk_update(updated_film,['order'])
        
    paginator = Paginator(films,7)
    page_number = len(film_pks_order)/ 7
    page_obj = paginator.get_page(page_number)
    context= {'films':films, 'page_obj':page_obj}
    return render(request,'partials/film-list.html',context)

@login_required
def detail(request,pk):
    user_film = get_object_or_404(UserFilms,pk=pk)
    context = {'userfilm':user_film}
    return render(request,'partials/film_detail.html',context)

@login_required
def upload_photo(request,pk):
    userfilm = get_object_or_404(UserFilms,pk=pk)
    photo = request.FILES.get('photo')
    userfilm.film.photo.save(photo.name, photo)
    
    context = {'userfilm':userfilm}
    return render(request,'partials/film_detail.html',context)
    