from django.utils import timezone


def format_time(utc_time):
    
    local_time = utc_time.astimezone(timezone.get_current_timezone())
    current_time = timezone.localtime()
    difference_time = current_time-local_time
    difference_days = difference_time.days
    difference_seconds = difference_time.seconds

    if difference_days < 0:
        return "From future"
    elif difference_days == 0 and difference_seconds < 60:
        return "Just Now"
    elif difference_days == 0:
        hours, remainder = divmod(difference_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        if hours > 0:
            return f"{hours} {'hour' if hours==1 else 'hours'}, {minutes} {'minute' if minutes==1 else 'minutes'} ago"
        elif minutes == 0:
            return f"{difference_seconds} {'second' if difference_seconds==1 else 'seconds'} ago"
        else:
            return f"{minutes} {'minute' if minutes==1 else 'minutes'} ago "
    elif difference_days < 365:
        return f"{difference_days} {'day' if difference_days==1 else 'days'} ago"
    else:
        years = difference_days//365
        return f"{years} {'year' if years==1 else 'years'} ago "
