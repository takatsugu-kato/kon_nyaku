"""
This module is for cron
"""
# from django.http import HttpResponse #only use for debug
from datetime import datetime
from dateutil.relativedelta import relativedelta
import lib.translator
from translate.models import File

# def set_delete_flag_for_debug(request): #only use for debug
#     today = datetime.today()
#     one_month_ago = today - relativedelta(months=1)
#     files = File.objects.filter(created_date__lte=one_month_ago).filter(delete_flag=False)
#     for file in files:
#         lib.translator.set_delete_flag(file.id)
#     return HttpResponse(files)

def set_delete_flag():
    """
    Set the delete flag for the item one month ago
    """
    today = datetime.today()
    one_month_ago = today - relativedelta(months=1)
    files = File.objects.filter(created_date__lte=one_month_ago).filter(delete_flag=False)
    for file in files:
        lib.translator.set_delete_flag(file.id)
