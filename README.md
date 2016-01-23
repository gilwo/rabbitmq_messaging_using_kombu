# rabbitmq_messaging_using_kombu
example of using various feature of rabbitMQ messaging system using kombu

Description
-----------
this is a sample producer/consumer with topic exchange and multi routing keys using
bound declared queus and timeout per queue
also there is a sample on how to add on the fly additional binding to exisiting queue

### Usage
use message_generator.py to generate messages:
```
python mwssage_generator.py | kombu_topics_prod.py
```
or without the generator and then you can pass manually messages (watch the format so it will get to the right place)


consumer can be called without any args to get the list of explicit queues available
it can be also called with wildcard :</br>
```
python kombu_topics_cons.py '#'
```
or
```
python kombu_topics_cons.py '*.info'
```
