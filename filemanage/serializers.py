from FileServerModel.models import TopicFile, ChatRoomFile
# from ChatServerModel.models import TopicMessage
from chat.models import TopicMessage, ChatRoomMessage

from rest_framework.serializers import ModelSerializer, SerializerMethodField


class TopicMessageSerializer(ModelSerializer):
    sender = SerializerMethodField()

    class Meta:
        model = TopicMessage
        fields = '__all__'

    def get_sender(self, obj):
        return obj.user_id.user_name


class TopicFileUploadSerializer(ModelSerializer):

    class Meta:
        model = TopicFile
        fields = ('user', 'message', 'file', 'origin_filename')
        read_only_fields = ('created_time', )


class TopicFileDownloadSerializer(ModelSerializer):

    class Meta:
        model = TopicFile
        fields = ('user', 'message', 'file')
        read_only_fields = ('created_time', )

####################################################################


class ChatRoomMessageSerializer(ModelSerializer):
    sender = SerializerMethodField()

    class Meta:
        model = ChatRoomMessage
        fields = '__all__'
        # fields = ('sender', 'chatRoom', 'contents', 'created_time')

    def get_sender(self, obj):
        return obj.user.user_name


class ChatRoomFileUploadSerializer(ModelSerializer):

    class Meta:
        model = ChatRoomFile
        fields = ('user', 'message', 'file', 'origin_filename')
        read_only_fields = ('created_time', )


class ChatRoomFileDownloadSerializer(ModelSerializer):

    class Meta:
        model = ChatRoomFile
        fields = ('user', 'message', 'file')
        read_only_fields = ('created_time', )