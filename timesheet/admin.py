from django.contrib import admin
from django.http import HttpResponse
from .views import ExportDataCSVAPIView
from rest_framework import status
from common import rest_utils
from django.urls import path
# class ExportDataAdminView(admin.site.AdminView):

#     def get(self, request, *args, **kwargs):
#         start_date_str = request.GET.get('start_date')
#         end_date_str = request.GET.get('end_date')
#         try:
#             # Call the ExportDataCSVAPIView to generate the CSV file
#             view = ExportDataCSVAPIView.as_view()
#             response = view(request)
#             # Return the CSV file as a downloadable file in the browser
#             response['Content-Disposition'] = 'attachment; filename="timesheet.xls"'
#             return response

#         except Exception as e:
#             message = rest_utils.HTTP_REST_MESSAGES["500"]
#             return rest_utils.build_response(
#                 status.HTTP_500_INTERNAL_SERVER_ERROR, message, data=None, errors=str(e)
            # )

# class ExportDataAdminView(admin.AdminSite):

#     def get_urls(self):
#         urls = super().get_urls()
#         urls += [
#             path('export_data_csv/', self.admin_view(ExportDataCSVAPIView.as_view()), name='export_data_csv')
#         ]
#         return urls
    

# admin.site.register_view('export_data_csv', view_class=ExportDataAdminView, name='Export Data CSV')