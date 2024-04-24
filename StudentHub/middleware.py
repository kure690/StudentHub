# from django.utils import timezone
# from django.contrib.auth import logout
# import datetime

# # Example datetime object
# current_datetime = datetime.datetime.now()

# # Convert datetime object to string using strftime
# formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")


# class AutoLogoutMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.user.is_authenticated:
#             last_activity = request.session.get('last_activity')
#             if last_activity:
#                 idle_time = timezone.now() - last_activity
#                 if idle_time.seconds > settings.SESSION_EXPIRE_SECONDS:
#                     logout(request)
#                     del request.session['last_activity']
#                     return self.get_response(request)
#         request.session['last_activity'] = timezone.now()
#         return self.get_response(request)
