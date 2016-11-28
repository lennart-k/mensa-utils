from datetime import date

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from fuzzywuzzy import fuzz

from mensautils.canteen.models import Serving, Notification


def send_notifications():
    now = timezone.now()
    today = date.today()
    relevant_servings = Serving.objects.filter(date=today, notified=False)
    notification_objs = Notification.objects.all()
    notified = set()
    for notification in notification_objs:
        for serving in relevant_servings.all():
            if (fuzz.partial_token_set_ratio(serving.dish.name, notification.pattern) >=
               settings.FUZZY_MIN_RATIO):
                subject = 'Mensabenachrichtigung: {} in {}'.format(
                    serving.dish.name, serving.canteen.name)
                message = '''Das Gericht {} wird heute in der Mensa {} zu einem Preis von {} € angeboten.

Du erhältst diese Nachricht, weil Du unter https://mensa.mafiasi.de eine
Benchrichtigung mit der Suchregel "{}" angelegt hast.'''.format(
                    serving.dish.name, serving.canteen.name, serving.price,
                    notification.pattern)
                send_mail(subject, message, settings.NOTIFICATION_FROM_ADDRESS,
                          [notification.user.email], fail_silently=False)
                notified.add(notification.pk)
                break  # skip more notifications for this user notification
    notification_objs.filter(pk__in=notified).update(last_notified=now)
    relevant_servings.update(notified=True)
