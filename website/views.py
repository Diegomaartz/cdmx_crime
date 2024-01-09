import folium, requests
from folium.plugins import FastMarkerCluster
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddReportForm, ProfilePicForm
from .models import crimeData, Profile
from django.core.paginator import Paginator
from django.contrib.auth.models import User


from django.http import JsonResponse


import googlemaps
import json
from django.conf import settings

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter

from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string


from django.core.mail import send_mail, EmailMessage

def home(request):
        if request.method == 'POST':
                # email = request.POST['email']
                # username = request.POST['username']
                # password = request.POST['password']
                username = request.POST.get('username')
                password = request.POST.get('password')

                # user = authenticate(request, email=email, password=password)
                user = authenticate(request, username=username, password=password)
                if user is not None:
                        login(request,user)
                        messages.success(request, "Has iniciado sesion!")
                        print("Login succesfully")
                        return redirect('home_news')
                else:
                        messages.success(request, "Ha ocurrido un error!")
                        print("Login unsuccsesfully")

                        return redirect('home')
        else:
                return render(request, 'home.html', {})

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Has cerrado sesion!")
        return redirect('home')
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            #Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request,user)
            messages.success(request, "Has iniciado sesion!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form':form})
    return render(request, 'register.html', {'form':form})

def profile(request):
    if request.user.is_authenticated:
        username = request.user.username
        user_reported_crimes = crimeData.objects.filter(user_report=username).values()
        return render(request, 'profile.html', {'user_reported_crimes': user_reported_crimes})
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')

def crime_cdmx(request):
    if request.user.is_authenticated:
        crimes = crimeData.objects.all().order_by('-user_report')
        # page = request.GET.get('page')
        return render(request, 'all_crimes.html',{
                                        'crimes':crimes,
                                        # 'page': page
                                        # 'crimes_pag': crimes_pag
                                        })
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')

def map_crimes(request):
    if request.user.is_authenticated:
        crimes = crimeData.objects.all()

        crime_data_list = [
            {'latitud': crimespot.latitud.replace(',', '.'),   #0
            'longitud': crimespot.longitud.replace(',', '.'),  #1
            'delito': crimespot.delito,                        #2
            'alcaldia': crimespot.alcaldia_hecho,              #3
            'fecha': crimespot.fecha_hecho,                    #4
            'user_report': crimespot.user_report,              #5
            'direccion': crimespot.direccion                   #6
            }   
            for crimespot in crimes
        ] 
        
        data = [(crime['latitud'], crime['longitud'],crime['delito'], crime['alcaldia'], crime['fecha'], crime['user_report'], crime['direccion']) for crime in crime_data_list]

        callback = """ \
        function (row, element){
            var icon, marker;

            icon = L.AwesomeMarkers.icon({
                icon: "map-marker", markerColor: "red"
            });
            marker = L.marker(new L.LatLng(row[0], row[1]));
            marker.setIcon(icon);

            var popupContent = "<p><b>Reportado por: </b> @" +row[5] + "</p>" +
                            "<p><b>Delito: </b>" + row[2] + "</p>" +
                            "<p><b>Alcaldía: </b>" + row[3] + "</p>" +
                            "<p><b>Fecha: </b>" + row[4] + "</p>" +
                            "<p><b>Direccion: </b>" + row[6] + "</p>" +
                            "<p><b>Location: </b>" + row[0] + " / " + row[1] + "</p>";
            marker.bindPopup(popupContent);

            return marker;
        };
        """

        mp = folium.Map(location=[19.432608, -99.133209], zoom_start=9)

        FastMarkerCluster(data=data, callback=callback).add_to(mp)

        context = {'map': mp._repr_html_()}
        return render(request, 'map_crimes.html', context)
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')

def news_api(request):
    if request.user.is_authenticated:
        url_top_mx_headlines = "https://newsapi.org/v2/everything?q=mexico&from=2023-12-20&to=2024-01-01&sortBy=popularity&apiKey=4940218b125845968afb458c5c9d2713"
        news_crimes = requests.get(url_top_mx_headlines).json()
        
        article = news_crimes['articles']
        desc = []
        title = []
        img = []
        url_new = []
        
        for i in range(len(article)):
                title.append(article[i]['title'])
                desc.append(article[i]['description'])
                img.append(article[i]['urlToImage'])
                url_new.append(article[i]['url'])
                
        news_crimes = zip(title, desc, img, url_new)
        return render(request, 'home_news.html', {'news_crimes':news_crimes})
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home')
    
def report_crime(request):
    if request.user.is_authenticated:
        username = request.user.username
        form = AddReportForm(request.POST or None, initial={'user_report':username})
        if request.method == 'POST':
            if form.is_valid():
                direccion = form.cleaned_data['direccion']

                latitud, longitud = get_lat_lng(direccion)
                
                form.instance.latitud = latitud
                form.instance.longitud = longitud

                report_crime = form.save()

                messages.success(request, "Crimen Reportado!")
                return redirect('home_news')
        return render(request, 'report_crime.html', {'form': form})
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')

def get_lat_lng(address):
    gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    result = gmaps.geocode(address)
    if result and 'geometry' in result[0] and 'location' in result[0]['geometry']:
        location = result[0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        return str(lat), str(lng)
    else:
        return None, None
    
def update_reported_crime(request, pk):
    if request.user.is_authenticated:
        reported_crime = crimeData.objects.get(id=pk)
        form = AddReportForm(request.POST or None, instance=reported_crime)
        if form.is_valid():
            form.save()
            messages.success(request, "El reporte ha sido actualizado")
            return redirect('home_news')
        return render(request, 'update_reported_crime.html', {'form':form})

    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')         

def delete_reported_crime(request, pk):
    if request.user.is_authenticated:
        delete_it = crimeData.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Reporte Eliminado")
        return redirect('home_news')
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')

def see_reported_crime(request, pk):
    if request.user.is_authenticated:
        reported_crime = crimeData.objects.get(id=pk)
        return render(request, 'see_reported_crime.html', {'reported_crime':reported_crime}) 
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')      
    
    
    
# def profile(request):
#     if request.user.is_authenticated:
#         username = request.user.username
#         user_reported_crimes = crimeData.objects.filter(user_report=username).values()
#         return render(request, 'profile.html', {'user_reported_crimes': user_reported_crimes})
#     else:
#         messages.success(request, "Debes Iniciar Sesion!")
#         return redirect('home_news')

def map_specific_crime(request, pk):
    if request.user.is_authenticated:
        specific_crime = crimeData.objects.get(id=pk)
        crimes = crimeData.objects.all()

        print(crimes)

        crime_data_list = [
            {'latitud': crimespot.latitud.replace(',', '.'),   #0
            'longitud': crimespot.longitud.replace(',', '.'),  #1
            'delito': crimespot.delito,                        #2
            'alcaldia': crimespot.alcaldia_hecho,              #3
            'fecha': crimespot.fecha_hecho,                    #4
            'user_report': crimespot.user_report,              #5
            'direccion': crimespot.direccion                   #6
            }   
            for crimespot in crimes
        ] 
        
        data = [(crime['latitud'], crime['longitud'],crime['delito'], crime['alcaldia'], crime['fecha'], crime['user_report'], crime['direccion']) for crime in crime_data_list]

        callback = """ \
        function (row, element){
            var icon, marker;

            icon = L.AwesomeMarkers.icon({
                icon: "map-marker", markerColor: "red"
            });
            marker = L.marker(new L.LatLng(row[0], row[1]));
            marker.setIcon(icon);

            var popupContent = "<p><b>Reportado por: </b> @" +row[5] + "</p>" +
                            "<p><b>Delito: </b>" + row[2] + "</p>" +
                            "<p><b>Alcaldía: </b>" + row[3] + "</p>" +
                            "<p><b>Fecha: </b>" + row[4] + "</p>" +
                            "<p><b>Direccion: </b>" + row[6] + "</p>" +
                            "<p><b>Location: </b>" + row[0] + " / " + row[1] + "</p>";
            marker.bindPopup(popupContent);

            return marker;
        };
        """

        mp = folium.Map(location=[specific_crime.latitud.replace(',', '.'), specific_crime.longitud.replace(',', '.')], zoom_start=55)

        FastMarkerCluster(data=data, callback=callback).add_to(mp)

        context = {'map': mp._repr_html_()}
        return render(request, 'map_specific_crime.html', context)
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
               
        user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, "Tu perfil ha sido actualizado!")
            return redirect('home_news')
        return render(request, "actualizar_perfil.html", {'user_form' : user_form, 'profile_form' : profile_form})
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home')
    
#Falta darle diseño al pedeefe
def generate_pdf_specific_report(request, pk):
    if request.user.is_authenticated:
        specific_crime = crimeData.objects.get(id=pk)
   
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)

        c.translate(cm, cm)
        c.setFont("Helvetica", 14)
        c.setStrokeColorRGB(1, 0, 0)  # Cambia el color de las líneas rectas a rojo
        c.setFillColorRGB(0, 0, 0)  # Color de la fuente

        # c.drawImage('website/static/logo.png', cm, cm)

        # Coloca el logo_b en la esquina superior derecha con una dimensión de 150x150 pixeles
        c.drawImage('website/static/logo_b.jpg', 6.3 * cm, 8.3 * cm, width=150, height=150)

        c.drawString(0, cm, "Ajajsjsj vete alv oscar ya jala este pedo XDDD")
        c.drawString(0, 0, "No mames no ce que estoy haciendo vlt vltv vtlv")
        c.drawString(0, 5 * cm, f'{specific_crime.direccion}')
        c.setFillColorRGB(0, 0, 0)  # Color de la fuente
        c.line(0, 2 * cm, 19 * cm, 2 * cm)
        c.line(0, 22 * cm, 19 * cm, 22 * cm)
        c.drawString(5.6 * cm, 9.5 * cm, 'Bill No :# 1234')
        
        from datetime import date
        dt = date.today().strftime('%d-%b-%Y')
        c.drawString(5.6 * cm, 9.3 * cm, dt)
        c.setFont("Helvetica", 8)
        c.drawString(3 * cm, 9.6 * cm, 'Tax No :# ABC1234')
        c.setFillColorRGB(1, 0, 0)  # Color de la fuente
        c.drawString(0, -0.5 * cm, u"\u00A9" + " plus2net.com")
        c.rotate(45)  # Rotar 45 grados
        c.setFillColorCMYK(0, 0, 0, 0.08)  # Color de la fuente CYAN, MAGENTA, YELLOW y BLACK
        c.setFont("Helvetica", 100)  # Estilo y tamaño de la fuente
        c.drawString(2 * cm, 1 * cm, "CDMX-CRIME-OFFICIAL-REPORT")  # Texto escrito
        c.rotate(-45)  # Restaurar la rotación 
            
        c.setFillColorRGB(0, 0, 1)
        c.setFont("Helvetica", 16)
        c.drawString(2 * cm, 4 * cm, 'This is my product')
        c.showPage()
        c.save()
        
        buf.seek(0)
        
        return FileResponse(buf, as_attachment=True, filename=f'CRIMEN-REPORTADO-{pk}.pdf')



def send_mail_ejemplo(request):
    subject = "No responder yeah prueba "
    message = "PRueba"
    from_email = settings.EMAIL_HOST_USER
    receptor = ["pohege8453@roborena.com"]
    send_mail(subject, message, from_email, receptor)
    
    