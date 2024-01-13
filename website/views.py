import folium, requests
from folium.plugins import FastMarkerCluster
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddReportForm, ProfilePicForm
from .models import crimeData, User, Profile
from django.core.paginator import Paginator
from sklearn.cluster import KMeans
import numpy as np


from django.http import JsonResponse

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm 
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader


import googlemaps
import json
from django.conf import settings
from proyecto.settings import EMAIL_HOST_USER



from django.core.mail import send_mail
from django.core.mail import EmailMessage

# import leafmap

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
            email = form.cleaned_data['email']
            
            user = authenticate(username=username, password=password)
            mail_sender_registro_user(username, email)
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
                mail_sender_registro_crime(request)
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
            mail_sender_reporte_actualizado(request)
            messages.success(request, "El reporte ha sido actualizado")
            return redirect('home_news')
        messages.error(request, "Verifica todos los datos")
        return render(request, 'update_reported_crime.html', {'form':form})

    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')         

def delete_reported_crime(request, pk):
    if request.user.is_authenticated:
        delete_it = crimeData.objects.get(id=pk)
        delete_it.delete()
        mail_sender_reporte_eliminado(request)
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


def FastMarkerCluster_(data, num_clusters, max_iters=100):
    """
    Parámetros:
    - data: Un array de numpy que contiene las coordenadas de los puntos.
    - num_clusters: El número de clusters a formar.
    - max_iters: Número máximo de iteraciones.

    Retorna:
    - labels: Las etiquetas de cluster asignadas a cada punto de datos.
    - centroids: Las coordenadas de los centroides de los clusters.
    """
    centroids = data[np.random.choice(data.shape[0], num_clusters, replace=False)]

    for _ in range(max_iters):
        distances = np.linalg.norm(data[:, np.newaxis, :] - centroids, axis=2)

        labels = np.argmin(distances, axis=1)

        new_centroids = np.array([data[labels == i].mean(axis=0) for i in range(num_clusters)])

        if np.all(centroids == new_centroids):
            break

        centroids = new_centroids

    return labels, centroids

def map_specific_crime(request, pk):
    if request.user.is_authenticated:
        specific_crime = crimeData.objects.get(id=pk)
        crimes = crimeData.objects.all()

        # print(crimes)

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


def draw_text_with_line_breaks(c, text, x, y, max_width, font_size):
    lines = []
    current_line = ""
    current_width = 0

    for word in text.split():
        word_width = c.stringWidth(word, "Helvetica", font_size)
        if current_width + word_width < max_width:
            current_line += word + " "
            current_width += word_width
        else:
            lines.append(current_line.strip())
            current_line = word + " "
            current_width = word_width

    lines.append(current_line.strip())

    for line in reversed(lines):
        c.drawString(x, y, line)
        y -= c._leading


def generate_pdf_specific_report(request, pk):
    if request.user.is_authenticated:
        specific_crime = crimeData.objects.get(id=pk)
   
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)

        c.saveState()
        c.scale(1,-1)
        image_path = 'website/static/logo_r.png'
        image = ImageReader(image_path)

        c.drawImage(image, 15, -55, width=75, height=50)
        c.restoreState()

        # c.save()

        #Propiedades
        c.translate(cm, cm)
        c.setFont("Helvetica", 14)
        c.setStrokeColorRGB(1, 0, 0)  
        c.setLineWidth(2) 
        c.setFillColorRGB(0, 0, 0) 

        #Marca de agua
        c.rotate(45)  
        c.setFillColorCMYK(0, 0, 0, 0.08)  
        c.setFont("Helvetica", 100) 
        c.drawString(5 * cm, 5 * cm, "CDMX-CRIME") 
        c.rotate(-45) 
        
        #Encabezado
        from datetime import date
        c.setFillColorRGB(0, 0, 0) 
        dt = date.today().strftime('%Y/%b/%d')
        c.setFillColorRGB(1, 0, 0)

        c.setFont("Helvetica-Bold", 20)
        c.drawString(4*cm, 0.5*cm, 'REPORTE DE CRIMEN - CRIME CDMX ')
        c.setFillColorRGB(0, 0, 0) 
        c.setFont("Helvetica-Bold", 14)

        c.drawString(11*cm, 2*cm, f'ID REPORTE:   {specific_crime.id}')
        c.drawString(0, 2*cm, f'Usuario: {specific_crime.user_report}')
        c.setFont("Helvetica", 14)
        c.drawString(11 * cm, 3 * cm, f'Emision del reporte: {dt}')
        c.drawString(0, 3*cm, f'Delito:   {specific_crime.delito}')

        #Cuerpo PDF
        
        c.setFont("Helvetica-Bold", 18)
        c.drawString(5*cm, 5.5*cm, 'DETALLES DEL INCIDENTE')
        c.setFont("Helvetica-Bold", 14)
        

        # Lugar del incidente
        c.drawString(0* cm, 8 * cm, 'Lugar del incidente: ')
        c.setFont("Helvetica", 14)
        max_width = 400  # Ajusta el ancho máximo permitido
        x_position = 5 * cm
        y_position = 10 * cm
        direccion_text = specific_crime.direccion
        draw_text_with_line_breaks(c, direccion_text, x_position, y_position, max_width, 14)


        c.setFont("Helvetica-Bold", 14)
        c.drawString(0* cm, 11 * cm, 'Fecha del incidente:  ')
        c.setFont("Helvetica", 14)
        c.drawString(5* cm, 12 * cm, f'{specific_crime.fecha_hecho}')
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0* cm, 14 * cm, 'Alcaldia del incidente:  ')
        c.setFont("Helvetica", 14)
        c.drawString(5* cm, 15 * cm, f'{specific_crime.alcaldia_hecho}')
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0* cm, 17 * cm, 'Colonia del incidente:  ')
        c.setFont("Helvetica", 14)
        c.drawString(5* cm, 18 * cm, f'{specific_crime.colonia_hecho}')


        #Pie de pagina
        c.setFillColorRGB(0.5, 0.5, 0.5) 
        c.setFont("Helvetica-Bold", 16)
        c.drawString(7*cm, 26*cm, 'CRIME CDMX - ESCOM')



        #Lineas
        
        c.line(0, 4 * cm, 19.5 * cm, 4 * cm)
        c.line(0, 24 * cm, 19.5 * cm, 24 * cm)
               
        c.setFillColorRGB(0, 0, 1)
        c.setFont("Helvetica", 16)
        c.showPage()
        c.save()
        
        buf.seek(0)
        
        return FileResponse(buf, as_attachment=True, filename=f'CRIMEN-REPORTADO-{pk}.pdf')
    

def mail_sender_registro_user(username, email):
    subject = f'BIENVENIDO A CRIME-CDMX {username}'
    message = "GRACIAS A TI PODREMOS HACER DE LA CIUDAD DE MÉXICO UN LUGAR MAS SEGURO!"
    recipient_list = [f'{email}']
    send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)

def mail_sender_registro_crime(request):
    if request.user.is_authenticated:
        username = request.user.username
        email = request.user.email
        subject = f'CRIMEN REPORTADO - CRIME-CDMX'
        message = f"{username}: !GRACIAS A TI PODREMOS HACER DE LA CIUDAD DE MÉXICO UN LUGAR MAS SEGURO!"
        recipient_list = [f'{email}']
        send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)
    
def mail_sender_reporte_actualizado(request):
    if request.user.is_authenticated:
        username = request.user.username
        email = request.user.email
        subject = f'REPORTE DE CRIMEN ACTUALIZADO - CRIME-CDMX'
        message = f"{username}: SE HAN ACTUALIZADO LOS DATOS DE TU REPORTE, ESPERAMOS SIGAS AYUDÁNDONOS A HACER MÁS SEGURA LA CIUDAD DE MÉXICO"
        recipient_list = [f'{email}']
        send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)
    
def mail_sender_reporte_eliminado(request):
    if request.user.is_authenticated:
        username = request.user.username
        email = request.user.email
        subject = f'REPORTE DE CRIMEN ELIMINADO - CRIME-CDMX'
        message = f"{username}: SE HA ELIMINADO TU REPORTE, ESPERAMOS SIGAS AYUDÁNDONOS A HACER MÁS SEGURA LA CIUDAD DE MÉXICO"
        recipient_list = [f'{email}']
        send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)


def update_user_profile(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        # profile_user = Profile.objects.get(user__id=request.user.id)
        user_form = SignUpForm(request.POST or None, instance = current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None)
        # if user_form.is_valid() and profile_form.is_valid():
        if profile_form.is_valid():
            # user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, "Usuario Actualizado")
            return redirect('home_news')      
        # return render(request, "update_user_profile.html", {"user_form" : user_form, "profile_form": profile_form})
        return render(request, "update_user_profile.html", {"profile_form": profile_form})
    else:
        messages.success(request, "Debes Iniciar Sesion!")
        return redirect('home_news')         