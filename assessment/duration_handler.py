from django.utils import timezone
import datetime


class DayTime(datetime.time):
    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    @property
    def time(self):
        return datetime.time(hour=self.hour, minute=self.minute, second=self.second)

    def __str__(self):
        try:
            return f"{self.day} days,  {self.time.strftime('%H:%M:%S')}"
        except AttributeError:
            return f"{self.time.strftime('%H:%M:%S')}"


class AssessmentDurationHandler:
    def __init__(self, duration, script_timestamp):
        self.duration = duration
        self.script_timestamp = script_timestamp

    def get_start_time(self):
        return self.script_timestamp

    def get_used_time(self):
        return timezone.now() - self.get_start_time()

    @property
    def used_time(self):
        return get_time_obj_from(self.get_used_time())

    def get_remaining_time(self):
        if self.get_used_time() >= self.duration:
            return None
        else:
            return self.duration - self.get_used_time()

    @property
    def remaining_time(self):
        return get_time_obj_from(self.get_remaining_time())

    def __bool__(self):
        if self.duration is not None:
            return bool(self.duration)
        else:
            return False

    def __gt__(self, other):
        if other:
            return self.duration > other

    def __lt__(self, other):
        if other:
            return self.duration < other

    def get_duration_time_obj(self):
        return get_time_obj_from(self.duration)

    @property
    def hour(self):
        return self.duration.seconds // 3600

    @property
    def minute(self):
        return (self.duration.seconds // 60) % 60

    @property
    def seconds(self):
        return self.duration.seconds % 60

    @property
    def is_time_up(self):
        if self.duration:
            return self.get_used_time() >= self.duration
        else:
            return False

    @property
    def end_time(self):
        try:
            return timezone.now() + self.get_remaining_time()
        except TypeError:
            now = timezone.now()
            return timezone.timedelta(days=now.day, hours=now.hour, minutes=now.minute, seconds=now.second)

    def get_duration_str(self):
        return get_time_obj_from(self.duration).strftime("%H:%M:%S")


def get_time_obj_from(timedelta):
    try:
        if timedelta and timedelta.days < 0:
            return -1
        elif timedelta:
            time = datetime.time(hour=timedelta.seconds // 3600,
                                 minute=(timedelta.seconds // 60) % 60,
                                 second=timedelta.seconds % 60
                                 )

            obj = DayTime(hour=time.hour, minute=time.minute, second=time.second)
            obj.day = timedelta // datetime.timedelta(days=1)
            return obj
    except AttributeError as err:
        raise Exception("datetime.timedelta, django.utils.timezone.timedelta expected. but got %s \n %s" % (timedelta, err))


class AssessmentDueDateHandler:
    def __init__(self, due_datetime: timezone.datetime, minimum_minutes=None):
        self.due_datetime = due_datetime
        self.minimum_minutes = minimum_minutes

    @property
    def is_due(self):
        if self:
            return timezone.now() >= self.due_datetime
        else:
            return False

    def __bool__(self):
        if self.minimum_minutes and self.minimum_minutes > self.due_datetime:
            return False

        return bool(self.due_datetime)

    def remaining_time(self):
        """
        :return the time remaining for the due datetime to end.
        """
        if self.is_due:
            return 0
        elif self.due_datetime:
            return self.due_datetime - timezone.now()

    @property
    def get_remaining_time(self):
        return get_time_obj_from(self.remaining_time())

    def __gt__(self, other):
        if isinstance(other, AssessmentDurationHandler):
            if other:
                return self.remaining_time() > other

    def __lt__(self, other):
        if isinstance(other, AssessmentDurationHandler):
            if other:
                return self.remaining_time() < other

    def time_left_object(self):
        """

        :return: (days, hours, minutes, seconds)
        """
        return self.get_remaining_time
