from django.urls import path
from records import views as record_views

app_name = 'records'

urlpatterns = [
    path('', record_views.upload, name="upload_view"),
    path('list/', record_views.Updated_New_View.as_view(), name="list_view"),
    path('delete/', record_views.Delete_all, name="delete_view")
]