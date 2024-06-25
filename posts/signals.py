from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Notification, OpenedNotification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=Notification)
def notification_handler(sender, instance , created, **kwargs):
    channel_layer = get_channel_layer()
    if created:
        
        # recipient_id = instance.recipient.id
        # OpenedNotification.objects.filter(user=follows).update(noti_count=F('noti_count')+1)
        # notif_isnot_seen = Notification.objects.filter(is_seen=False, recipient_id=recipient_id).count()
        # async_to_sync(channel_layer.group_send)(
        #     f'notification_{recipient_id}', {'type':'send.notifications', 'message':notif_isnot_seen}
        # 
        # )

        recipient_id = instance.recipient.id
        not_seen_notif_count = OpenedNotification.objects.get(user=instance.recipient)
        not_seen_notif_count.noti_count += 1
        not_seen_notif_count.save()

        async_to_sync(channel_layer.group_send)(
            f'notification_{recipient_id}', {'type':'send.notifications', 'message':not_seen_notif_count.noti_count}
        )


@receiver(post_delete, sender=Notification)
def notification_handler_deletion(sender, instance, **kwargs):
    
    # channel_layer = get_channel_layer()
    # recipient_id = instance.recipient.id
    # OpenedNotification.objects.filter(user=post.user).update(noti_count=F('noti_count')-1)
    # async_to_sync(channel_layer.group_send) (
    #     f'notification_{recipient_id}', {'type':'send.notifications', 'message':notif_isnot_seen}
    # )
    channel_layer = get_channel_layer()
    recipient_id = instance.recipient.id

    not_seen_notif_count = OpenedNotification.objects.get(user=instance.recipient)
    if not_seen_notif_count.noti_count >0:
        not_seen_notif_count.noti_count -= 1
        not_seen_notif_count.save()
        async_to_sync(channel_layer.group_send)(
                f'notification_{recipient_id}', {'type':'send.notifications', 'message':not_seen_notif_count.noti_count}
        )
    
    