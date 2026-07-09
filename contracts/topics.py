class UserServiceTopics:
    AGGREGATE_TYPE = "user"
    TOPIC = "userservice.user"


class SubscriptionServiceTopics:
    AGGREGATE_TYPE = "subscription"
    TOPIC = "subscriptionservice.subscription"


class DBServiceTopics:
    AGGREGATE_TYPE = "dbquery"
    TOPIC = "dbservice.dbquery"
