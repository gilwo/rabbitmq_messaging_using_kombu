from enum import Enum
import time


class lvl(Enum):
    log_error = 1
    log_warning = 2
    log_info = 3
    log_debug = 4
    log_trace = 5
    event_alert = 6
    event_activity = 7
    event_trace = 8

#lvl_list = [(x.name, x.value) for x in lvl]
lvl_list = [x.name for x in lvl]

count = 0

while True:
    print("msg (%s : %s) route %s" % (count,
                                      lvl_list[count % len(lvl_list)],
                                      lvl_list[count % len(lvl_list)].replace('_', '.')))
    count += 1
    if count % 20 == 0:
        time.sleep(2)
