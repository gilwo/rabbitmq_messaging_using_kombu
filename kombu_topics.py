from kombu import Exchange, Queue

PRI_TOPIC_NAME = 'primary_topic'
priTopicXchg = Exchange(name=PRI_TOPIC_NAME,
                        type='topic',
                        durable=True,
                        deilvery_mode="persistent")

priTopicQinfo = [
    {'name': 'L_TRACE',    'routing_key': 'log.trace'},
    {'name': 'L_DEBUG',    'routing_key': 'log.debug'},
    {'name': 'L_WARNING',  'routing_key': 'log.warning'},
    {'name': 'L_INFO',     'routing_key': 'log.info'},
    {'name': 'E_TRACE',    'routing_key': 'event.trace'},
    {'name': 'E_ACTIVITY', 'routing_key': 'event.activity'},
    {'name': 'E_ALERT',    'routing_key': 'event.alert'},
    {'name': 'E_INFO',     'routing_key': 'event.info'}
]

q_expires = {'x-expires': 1*60*1000}   # 60 secs
priTopicExplicitQs = list(map(lambda x: Queue(x['name'],
                                              priTopicXchg,
                                              routing_key=x['routing_key'],
                                              queue_arguments=q_expires),
                              priTopicQinfo))

#priTopicPartialImplicitQs = [
#    Queue('ALL_LOGS',   priTopicXchg, routing_key='log.*'),
#    Queue('ALL_TRACE',  priTopicXchg, routing_key='*.trace'),
#    Queue('ALL',        priTopicXchg, routing_key='#')
#]

allQs = priTopicExplicitQs # + priTopicPartialImplicitQs


msgs = [
    {'topic': PRI_TOPIC_NAME, 'routing': 'log.trace',      'msg': "trace log message"},
    {'topic': PRI_TOPIC_NAME, 'routing': 'log.debug',      'msg': "debug log message"},
    {'topic': PRI_TOPIC_NAME, 'routing': 'log.warning',    'msg': "warning log message"},
    {'topic': PRI_TOPIC_NAME, 'routing': 'log.info',       'msg': "info log message"},
    {'topic': PRI_TOPIC_NAME, 'routing': 'event.trace',    'msg': "trace event message"},
    {'topic': PRI_TOPIC_NAME, 'routing': 'event.activity', 'msg': "activity event message"},
    {'topic': PRI_TOPIC_NAME, 'routing': 'event.alert',    'msg': "alert event message"},
    {'topic': PRI_TOPIC_NAME, 'routing': 'event.info',     'msg': "info event message"}
]

# localhost single host
_amqp_hosts1 = [
    'amqp://guest:guest@localhost:5672//'
]

# cluster mode
_amqp_hosts2 = [
    'amqp://guest:guest@10.0.0.1:5672//',
    'amqp://guest:guest@10.0.0.2:5672//',
    'amqp://guest:guest@10.0.0.3:5672//'
]

# cluster mode on the same machien
_amqp_hosts3 = [
    'amqp://guest:guest@localhost:56722//',
    'amqp://guest:guest@localhost:56723//'
]
amqp_hosts = _amqp_hosts3


def on_ens_conn_err_cb(exception, interval):
    print("got connection error cb, error:[%s], interval:[%s]" %
          (repr(exception), interval))

