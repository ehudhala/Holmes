import json

from arrow import Arrow

from holmes.config import COMPANY_ID, BRANCH_ID, USER_ID
from holmes.utils import create_logger, ISRAEL_TZ, holmes_place_now, readable_time, CouldNotRegisterError, CouldNotGetActivitiesError

OPEN_FOR_REGISTRATION_STATUS = 'Open'
GET_ACTIVITIES_URL = 'http://api.holmesplace.co.il/WebSite/HPCalendar.aspx/GetFilteredActivities'

logger = create_logger(__name__)


class Activity(object):
    """
    An adapter between the activity json sent by HolmesPlace into a python object.
    Parsing the activity json happens here.
    """
    REGISTER_URL = 'http://api.holmesplace.co.il/WebSite/HPCalendar.aspx/RegisterMultiWithSeat'

    def __init__(self, activity_json):
        self.activity_json = activity_json

        self.time = self.parse_date(activity_json, 'lessonDate', 'lessonTime', '%Y/%m/%d')
        self.lesson_start_hour_string = activity_json['lessonStartHour']
        self.lesson_id = activity_json['lessonId']
        self.status = activity_json['lessonStatus']
        self.is_favorite = activity_json['isFavorite']
        self.require_reserve = activity_json['requireReserve']
        self.instructor_id = activity_json['instructorId']
        self.lesson_name = activity_json['lessonName']
        if self.require_reserve:
            self.registration_start_time = self.parse_date(activity_json, 'dateBeforeReg', 'timeBeforeReg', '%d/%m')
            self.registration_start_time = self.registration_start_time.replace(year=self.time.year)

    def parse_date(self, activity_json, date_name, time_name, date_format):
        """
        Holmes Place uses dates in weird ways.
        They don't have any convention about formatting,
        and it is split between two variables of the date and time.
        """
        date = Arrow.strptime(activity_json[date_name], date_format, tzinfo=ISRAEL_TZ)
        time = Arrow.strptime(activity_json[time_name], '%H:%M', tzinfo=ISRAEL_TZ)
        return date.replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)

    def date_timestamp_in_micro(self):
        """
        This is copied from the Holmes Place javascript.
        Holmes Place use UTC time in micro seconds.
        """
        date = self.time.replace(hour=0, minute=0)
        return (date + date.utcoffset()).timestamp * 1000

    def register(self, session, reservation_names):
        """
        Registers the names given to the activity.
        """
        data = {
            "password": "",
            "companyId": COMPANY_ID,
            "branchId": BRANCH_ID,
            "userId": USER_ID,
            "lessonId": self.lesson_id,
            # They measure in microseconds
            "date": self.date_timestamp_in_micro(),
            "time": self.lesson_start_hour_string,
            "instructorId": self.instructor_id if self.instructor_id != 0 else None,
            "seatIds": None,
            "reservationNames": reservation_names
        }
        response = session.post(self.REGISTER_URL, json=data)

        response_content = response.json()['d']
        if not response_content['Success']:
            raise CouldNotRegisterError(u"Couldn't register to {}. The reason is: {}".format(
                self, response_content['Message']))

    def should_register(self):
        """
        Gets an activity,
        and returns whether we should register to the activity or not.
        """
        return (self.is_favorite and
                self.require_reserve and
                self.time > holmes_place_now())

    @property
    def readable_time(self):
        return readable_time(self.time)

    def __eq__(self, other):
        """
        Used for checking if an activity is already shceduled.
        An activity is uniquely identified by its time and lesson id.
        """
        return self.time == other.time and self.lesson_id == other.lesson_id

    def __unicode__(self):
        return u'Lesson {} with id {} at {}'.format(self.lesson_name, self.lesson_id, self.readable_time)


def get_week_activities(session, day_in_week):
    """
    Gets all the activities for the week of the given day.
    :param session: An authenticated session to HolmesPlace.
    :param day_in_week: A day in a week we want to get the activities of.
    :return: A list of activities.
    :rtype: list[dict[str,str]]
    """
    # TODO: add a test that will alert us if they changed interface, currently we assume it has 'd'
    # TODO: improve hard-coded variables.
    data = {
        'companyId': COMPANY_ID,
        'branchId': BRANCH_ID,
        'userId': USER_ID,
        'activeModuleId': 7,
        'dayInWeek': day_in_week.strftime('%d/%m/%Y'),
        'instructorId': -1,
        'timeOfDay': '',
        'lessonType': -1,
        'diplayOnlyAvailable': False,
        'diplayOnlyFavorites': False,
        'cobrStr': ''
    }
    response = session.post(GET_ACTIVITIES_URL, json=data)
    response_json = json.loads(response.json()['d'])

    if not response_json['succsess']:
        raise CouldNotGetActivitiesError("Failed getting week activities. Response was not successful")

    logger.debug('Got the week activities for the week of {}'.format(day_in_week.strftime('%d/%m/%y')))
    return map(Activity, response_json['activityItemsArray'])


def get_current_and_next_week_activities(session):
    """
    Returns the activities of the current week, with the activities of the next week.
    We do it because we can register to sunday activities on thursday.
    """
    activities = get_week_activities(session, holmes_place_now())
    activities += get_week_activities(session, holmes_place_now().replace(days=+7))
    return activities

