from django.template import Library
from chat.models import Message
register = Library()


@register.filter(name="chat_count")
def count_user_chat_been_sent(from_user, to_user):
    return Message.objects.filter(from_user=from_user, to_user=to_user, read=False).count()

