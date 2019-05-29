#!/usr/bin/env python
# -*- coding: utf-8 -*-

import praw
import reddit
import os
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

reddit_bot = {
    "reply": (reddit.random_reply, PROBABILITIES["REPLY"]),
    "submit": (reddit.random_submission, PROBABILITIES["SUBMISSION"]),
    "delete": (reddit.delete_comments, PROBABILITIES["DELETE"]),
}


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

            for name, action in reddit_bot.items():
                time_diff_since_limit = int(time.time()) - RATE_LIMIT  # seconds
                if time_diff_since_limit != 0:
                    countdown(NEED_TO_WAIT)
                    break
                # reset
                NEED_TO_WAIT = 0
                try:
                    if prob(action[1]):
                        log.info("making a random {}".format(name))
                        action[0]()
                except praw.exceptions.APIException as e:
                    log.info("was unable to {} - {}".format(name, e))
                    NEED_TO_WAIT = get_seconds_to_wait(str(e))
            if prob(PROBABILITIES["LEARN"]):  # chance we'll learn more
                log.info("going to learn")
                learn()

            # Wait 10 minutes to comment and post because of reddit rate limits
            countdown(1)
        log.info("end main loop")
