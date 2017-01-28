# coding=utf-8
import time
from sched import scheduler as Scheduler

from activities import get_current_and_next_week_activities
from authentication import create_session

from holmes.config import RESERVATION_NAMES
from holmes.utils import create_logger, holmes_place_now, readable_time, send_mail, HolmesPlaceException

DEFAULT_WAIT_TIME = 60
WAIT_EXPONENT = 1.5
# After about 6.5 hours we stop trying anymore.
MAX_WEIGHT_TIME = DEFAULT_WAIT_TIME * (WAIT_EXPONENT ** 12)

HOUR_SECONDS = 60 * 60

logger = create_logger(__name__)


def register_and_reschedule(scheduler, activity, reservation_names, wait_time=DEFAULT_WAIT_TIME):
    """
    Registers to an activity.
    If we fail to register, we try again in exponential backoff.
    Maybe the time on our server isn't synced with the time on Holmes Place,
    and then we will register a few minutes before,
    that's why we exponential backoff until we succeed.
    :param scheduler: The scheduler used to reschedule if we fail.
    :param activity: The activity to register to.
    :param reservation_names: The names to register to the activity.
    :param wait_time: How long to wait for the next try to register.
    """
    logger.info(u'Trying to register to {}'.format(activity))

    try:
        register_and_inform(activity, reservation_names)
    except HolmesPlaceException as e:
        if wait_time < MAX_WEIGHT_TIME:
            logger.exception(u"{}, trying again in {} seconds".format(e.message, wait_time))
            scheduler.enter(wait_time, 3, register_and_reschedule, (
                scheduler, activity, reservation_names, wait_time * WAIT_EXPONENT))
        else:
            logger.exception(u'Failed registering to {} too many times, stopping.'.format(activity))


def register_and_inform(activity, reservation_names):
    """
    Registers the activity, and then informs us that we registered by sending a mail.
    This is important because we don't want to register to an activity to wchich we won't go,
    so this mail is used to cancel the registration if we don't go.
    """
    session = create_session()
    activity.register(session, reservation_names)
    logger.info(u'Registered to {}'.format(activity))
    send_mail(u"Registered to {}".format(activity),
              u"You can cancel it at http://www.holmesplace.co.il/clubs_services/club/56676/lessons")


def schedule_activities(scheduler, scheduled=None):
    """
    Gets all the activities for the following weeks,
    and schedules a registration for them.
    It also schedules itself to run again in a few hours,
    so that if anything changes we will adjust.
    (This means this function is a loop)
    :param scheduler: The scheduler to schedule the registration with,
                      and the rerunning of the scheduling.
    :param scheduled: A list of all the activities that have already been scheduled.
                      Used so that we wont schedule an activity more than one time.
                      By default it is empty.
    """
    scheduled = scheduled or []

    logger.info(u'Scheduling Activities for {}'.format(readable_time(holmes_place_now())))
    try:
        for activity in get_activities_to_schedule(scheduled):
            schedule_activity_registration(activity, scheduler)
            scheduled.append(activity)
    except HolmesPlaceException:
        logger.exception("Couldn't get activities.")

    scheduler.enter(3 * HOUR_SECONDS, 1, schedule_activities, (scheduler, scheduled))


def schedule_activity_registration(activity, scheduler, reservation_names=RESERVATION_NAMES):
    """
    Schedules an activity to be registered.
    IT is scheduled to be registered in the time its registration opens.
    """
    logger.info(u"scheduled a registration to {}. It will be registered to at {}".format(
        activity, readable_time(activity.registration_start_time)))

    scheduler.enterabs(
        activity.registration_start_time.timestamp, 2,
        register_and_reschedule, (scheduler, activity, reservation_names))


def get_activities_to_schedule(scheduled):
    """
    Gets all the activities for the following weeks,
    and returns those that still need to be scheduled.
    Activities need to be scheduled if they should be registered to
    and they haven't been scheduled to already.
    """
    session = create_session()
    activities = get_current_and_next_week_activities(session)
    return [activity for activity in activities
            if activity.should_register() and activity not in scheduled]


def schedule_forever():
    """
    Schedules activities registration forever :)
    """
    scheduler = Scheduler(time.time, time.sleep)
    schedule_activities(scheduler)
    try:
        scheduler.run()
    except KeyboardInterrupt:
        logger.debug('Got SIGTERM! Terminating...')


if __name__ == '__main__':
    schedule_forever()

