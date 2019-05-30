#!/usr/bin/env python
# -*- coding: utf-8 -*-

import praw
import reddit
import os
import time
from utils import (
    bytesto,
    countdown,
    prob,
    MAIN_DB,
    PROBABILITIES,
    get_public_ip,
    check_internet,
    MAIN_DB_MIN_SIZE,
    get_seconds_to_wait,
    reddit_bot_action,
    get_current_epoch,
)
from learn import learn
from logger import log
from requests import get

try:
    if not check_internet():
        log.error("internet check failed, do we have network?")
    ip = get_public_ip()
    log.info("My public IP address is: {}".format(ip))
except Exception as e:
    log.error("counld not check external ip")


RATE_LIMIT = 0
NEED_TO_WAIT = 0
log.info("------------new bot run--------------")
log.info("user is " + str(reddit.api.user.me()))

reddit_bot = [
    reddit_bot_action("reply", reddit.random_reply, PROBABILITIES["REPLY"], 0),
    reddit_bot_action(
        "submit", reddit.random_submission, PROBABILITIES["SUBMISSION"], 0
    ),
    reddit_bot_action("delete", reddit.delete_comments, PROBABILITIES["DELETE"], 0),
]


if __name__ == "__main__":
    log.info("db size size to start replying:" + str(bytesto(MAIN_DB_MIN_SIZE, "m")))
    while True:

        if os.path.isfile(MAIN_DB):
            size = os.path.getsize(MAIN_DB)
            log.info("db size: " + str(bytesto(size, "m")))
        else:
            size = 0

        if size < MAIN_DB_MIN_SIZE:  # learn faster early on
            log.info("fast learning")
            learn()
            try:
                log.info("new db size: " + str(bytesto(os.path.getsize(MAIN_DB), "m")))
            except:
                pass

            countdown(5)

        if (
            size > MAIN_DB_MIN_SIZE
        ):  # once we learn enough start submissions and replies
            log.info("database size is big enough")

            for action in reddit_bot:
                if action.rate_limit_unlock_epoch != 0:
                    if action.rate_limit_unlock_epoch > get_current_epoch():
                        log.info(
                            "{} hit RateLimit recently we need to wait {} seconds with this".format(
                                action.name,
                                action.rate_limit_unlock_epoch - get_current_epoch(),
                            )
                        )
                        continue
                    else:
                        action._replace(rate_limit_unlock_epoch=0)
                else:
                    if prob(action.probability):
                        log.info("making a random {}".format(action.name))
                        try:
                            action.action()
                        except praw.exceptions.APIException as e:
                            secs_to_wait = get_seconds_to_wait(str(e))
                            action._replace(
                                rate_limit_unlock_epoch=(
                                    get_current_epoch() + secs_to_wait
                                )
                            )
                            log.info(
                                "{} hit RateLimit, need to sleep for {} seconds".format(
                                    action.name, secs_to_wait
                                )
                            )
                        except Exception as e:
                            log.error(
                                "something weird happened, {}".format(e), exc_info=False
                            )
            if prob(PROBABILITIES["LEARN"]):  # chance we'll learn more
                log.info("going to learn")
                learn()

            # Wait 10 minutes to comment and post because of reddit rate limits
            countdown(1)
        log.info("end main loop")
