from kombu import Connection
from kombu_topics import *
import sys


def on_return(exception, exchange, routing_key, message):
    print('on_return occur:\n  exception[%s]\n  exchange[%s]\n'
          '  routing_key[%s]\n  message[%s]' %
            (exception, exchange, routing_key, message))


def queue_on_declare(name, messages, consumers):
    print("new queue declared: name[%s], messages[%s], consumers[%s]" %
            (name, messages, consumers))


def do_produce(use_predef_msgs=False):
    conn = Connection(amqp_hosts, failover_strategy='round-robin' )
    conn.ensure_connection(errback=on_ens_conn_err_cb)
    conn.connect()

    # bind xchg and Qs to the rmq connection, declare primary exchange
    bound_priTopicXchg = priTopicXchg(conn)
    bound_priTopicXchg.declare()
    """
    #  and all explicit Qs in rmq
    for i in priTopicExplicitQs:
        _bound_q = i(conn)
        try:
            _bound_q.declare()
        except Exception as e:
            print("unable to declare, exception type [%s], [%s]" %
                    (type(e), repr(e)))
            _bound_q.delete()
            _bound_q.declare()
    """

    producer = conn.Producer(serializer='json')

    if use_predef_msgs:
        for msg in msgs:
            if msg['topic'] == PRI_TOPIC_NAME:
                xchg = priTopicXchg
                qs = priTopicExplicitQs
            else:
                print("unknown topic [%s]" % msg['topic'])
     
            print("sending messages[%s], xchg[%s], topic[%s], routing[%s]"
                    % (msg['msg'], xchg, msg['topic'], msg['routing']))

            producer.publish(
                    msg['msg']
                    , exchange=xchg
                    , declare=[xchg] + qs  #  let declaration of the exchange and the explicit Qs
                    #,compression='zlib'
                    , compression='bzip2'
                    , routing_key=msg['routing']
                    # apparently expiration per message dont really work in kombu 3.0.32
                    #exipration=10 # 60*15 # 15 minutes
                    #,properties=properties
                    #,x-message-ttl=1000
                    )
     
            print("all predefined messages sent")

    try:
        while True:
            var = input('')
            print(var.split('route'))
            tmp = [i.strip(' ') for i in var.split('route')]
            if len(tmp) != 2:
                print("invalid msg [%s], need to be of form: [aaa bbb route x.y.z]" %
                      var)
                continue
            try:
                bound_priTopicXchg.publish(
                        bound_priTopicXchg.Message(tmp[0]),
                        routing_key=tmp[1]
                        )
            except conn.connection_errors + conn.channel_errors:
                print("connection [%s] went down , reconnect to the next one" %
                    conn.info())
                conn.close()
                conn.ensure_connection(errback=on_ens_conn_err_cb)
                bound_priTopicXchg = priTopicXchg(conn)
                bound_priTopicXchg.publish(
                    bound_priTopicXchg.Message(tmp[0]),
                    routing_key=tmp[1]
                )

    except (EOFError, KeyboardInterrupt):
        print("done")

if __name__ == '__main__':
    use_predef = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'imsg':
            use_predef = True
    do_produce(use_predef)
