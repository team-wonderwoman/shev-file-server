from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    TopicFileUploadView,
    TopicFileDownloadView,

    ChatRoomFileUploadView,
    ChatRoomFileDownloadView
)

# API endpoints
urlpatterns = format_suffix_patterns([

    # api/upload/topics/:topics_id/
    # [POST] user : user_pk
    url(r'^upload/topics/(?P<topic_id>\d+)/$', TopicFileUploadView.as_view()),

    # api/download/topics/:topics_id/:message_id
    url(r'^download/topics/(?P<topic_id>\d+)/(?P<message_id>\d+)/$',
        TopicFileDownloadView.as_view(),
        name='download_topicfile'),

    # api/upload/chatrooms/:chatroom_id/
    # [POST] user : user_pk
    url(r'^upload/chatrooms/(?P<chatroom_id>\d+)/$', ChatRoomFileUploadView.as_view()),

    # api/download/chatrooms/:chatroom_id/:message_id
    url(r'^download/chatrooms/(?P<chatroom_id>\d+)/(?P<message_id>\d+)/$',
        ChatRoomFileDownloadView.as_view(),
        name='download_chatroomfile')
])
