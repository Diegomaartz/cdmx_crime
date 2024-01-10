from . import views
from django.urls import path
from drf_spectacular.views import extend_schema

urlpatterns = [
    path('', views.home, name="home"),
    path('home_news/', views.news_api, name="home_news"),
    path('logout/', views.logout_user, name="logout"),
    path('register/', views.register_user, name="register"),
    path('profile/', views.profile, name="profile"),
    path('all_crimes/', views.crime_cdmx, name="all_crimes"),
    path('map_specific_crime/<int:pk>', views.map_specific_crime, name="map_specific_crime"),
    path('map_crimes/', views.map_crimes, name="map_crimes"),
    path('report_crime/', views.report_crime, name="report_crime"),
    path('update_reported_crime/<int:pk>', views.update_reported_crime, name="update_reported_crime"),
    path('delete_reported_crime/<int:pk>', views.delete_reported_crime, name="delete_reported_crime"),
    path('see_reported_crime/<int:pk>', views.see_reported_crime, name="see_reported_crime"),
    path('generate_pdf_specific_report/<int:pk>', views.generate_pdf_specific_report, name="generate_pdf_specific_report"),

    path('mail_Sender/', views.mail_Sender, name="mail_Sender"),



    # path('user_reports/', views.user_reports, name="user_reports"),
    # path('delete_report_crime/<int:pk>', views.delete_report_crime, name="delete_report_crime"),

]
