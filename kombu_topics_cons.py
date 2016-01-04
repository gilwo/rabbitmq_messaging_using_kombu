from kombu import Connection, Consumer, common
from kombu_topics import *
from pprint import pformat

allQsByName = ", ".join(list(map(lambda x: x.as_dict()['name'], allQs)))

count=0
bound_cons_Q = None

def pretty(obj):
    return pformat(obj, indent=4)

def on_msg_cb_2(body, message):
    # print("========= cb_2 ===========")
    # print("got message [%s], body[%s]" % (message, body))
    print("got message %d [%r]" % (count, body))
    if message.delivery_info['routing_key'] not in [x['routing_key'] for x in priTopicQinfo]:
        print("huston do we have a problem [%s]" % message.delivery_info['routing_key'])
        if message.delivery_info['routing_key'] == 'manage.queue.bind':
            print('manage requested Queue to bind to additional routing: [%s]' % body)
            global bound_cons_Q
            message.ack()
            bound_cons_Q.bind_to(exchange=priTopicXchg, routing_key=body)


def on_msg_cb_1(body, message):
    global count
    count +=1
    """
    print("========= cb_1 ===========")
    print('Received msg: %r' % (body, ))
    print('  propoerties:\n%s' % (pretty(message.properties), ))
    print('  delivery_info:\n%s' % (pretty(message.delivery_info), ))
    print('total msg till now [%d]' % count)
    """
    if count % 100 == 0:
        print('total msg till now [%d]' % count)
    #message.ack()

def on_message():
    pass


def do_consume(user_qs):

    print("about to listen no queues [%s]" %
          ", ".join(list(map(lambda x: x, user_qs))))

    conn = Connection(amqp_hosts, failover_strategy='round-robin')

    # try to get a connection no matter what
    while True:
        try:
            conn.ensure_connection(errback=on_ens_conn_err_cb)
            conn.connect()
        except Exception as e:
            print("connection error failed on exception [%s]" % repr(e))
            conn.release()
            continue
        if conn.connected:
            break
        else:
            print("connection failed in some way, retry")

    chan = conn.channel()

    global bound_cons_Q

    cons_Q = Queue(common.uuid(), queue_arguments=q_expires)
    bound_cons_Q = cons_Q(chan)
    bound_cons_Q.declare()
    # first bind to some control route
    bound_cons_Q.bind_to(priTopicXchg, routing_key='manage.#')
    for i in user_qs:
        if '*' in i or '#' in i:
            # create the wildcard route_key bind
            bound_cons_Q.bind_to(priTopicXchg, routing_key=i)
        else:
            for j in allQs:
                if i == j.as_dict()['name']:
                    bound_cons_Q.bind_to(priTopicXchg, routing_key=j.as_dict()['routing_key'])

    cons = Consumer(
            chan,
            accept=['json'],
            queues=bound_cons_Q,
            callbacks=[on_msg_cb_1, on_msg_cb_2]
            )

    print("queue set to [%s]" % bound_cons_Q.as_dict(recurse=True))
    cons.consume()
    while True:
        try:
            
            conn.drain_events()
        except conn.connection_errors + conn.channel_errors as e:
            print("connection [%s] went down (error[%s]), trying to "
                  "connect to the next one" % (conn.info(), repr(e)))
            conn.close()
            conn.release()
            conn.ensure_connection(errback=on_ens_conn_err_cb)
            conn.connect()

            chan = conn.channel()
            cons_Q.bind(chan)
            cons = Consumer(
                    chan,
                    accept=['json'],
                    queues=bound_cons_Q,
                    callbacks=[on_msg_cb_1, on_msg_cb_2]
                    )
            cons.consume()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("not enough argumetns")
        print("available explicit queues:")
        from pprint import pprint
        pprint(allQsByName)
        sys.exit(0)
    else:
        user_qs = []
        for i in sys.argv[1:]:
            if '*' in i or '#' in i:
                print("binding not fully operational yet in consumer")
                user_qs.append(i)
                continue
            if i == 'all':
                user_qs = allQsByName
                break
            if i not in allQsByName:
                print("[%s] is not available in %s" % (i , allQsByName))
                sys.exit(0)
            if i in user_qs:
                continue
            user_qs.append(i)
        if user_qs is []:
            print("user queues empty")
            sys.exit(0)
        print("listening on queues: %s" % user_qs)
    try:
        do_consume(user_qs)
    except KeyboardInterrupt:
        print('done')
