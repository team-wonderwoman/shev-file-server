import requests
from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import (
    FileUploadParser,
    MultiPartParser,
    FormParser
)
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer

from ShevFileServer.settings import MEDIA_ROOT
from chat.models import *
from AuthSer.models import User
from FileServerModel.models import TopicFile, ChatRoomFile

from .serializers import (
    TopicMessageSerializer,

    TopicFileUploadSerializer,
    TopicFileDownloadSerializer,

    ChatRoomMessageSerializer,

    ChatRoomFileUploadSerializer,
    ChatRoomFileDownloadSerializer,
)

from common.const import const_value, status_code

CHAT_SERVER_IP = "192.168.0.33"
CHAT_SERVER_POST = "9000"
CHAT_SERVER = CHAT_SERVER_IP + ":" + CHAT_SERVER_POST + "/"
CHAT_SERVER_ROOT_API = "api/group/"
# EX. 192.168.0.33:9000/api/group/chatroomfile/"


class TopicFileUploadView(APIView):
    queryset = TopicFile.objects.all()
    # parser_classes = (FileUploadParser,)
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = TopicFileUploadSerializer

    def post(self, request, format=None, *args, **kwargs):
        print("[[FileUploadView]] post")

        file = request.data['file']
        origin_filename = file.name

        user_id = request.data['user']
        user = User.objects.get(pk=user_id)

        topic_id = self.kwargs['topic_id']  # data in url
        topic = Topic.objects.get(pk=topic_id)

        # TopicMessage 저장 & Serializer 형태로 변환
        topicMessage = TopicMessage.objects.create(
            user_id=user,
            topic_id=topic,
            contents=origin_filename,
            is_file=True)
        messages_serializer = TopicMessageSerializer(topicMessage)

        # TopicFile 저장
        request.data['message'] = topicMessage.id
        request.data['origin_filename'] = origin_filename
        file_serializer = TopicFileUploadSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()

            # websocket으로 message send 하기 위해 필요한 정보를 ShevChatServer로 보낸다.
            send_data = {
                'room_id': topic_id,
                'username': user.user_name,
                'message': messages_serializer.data
            }
            data_json = json.dumps(send_data)
            # payload = {'json_payload': data_json}
            print(data_json)

            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

            res = requests.post("http://" + CHAT_SERVER + CHAT_SERVER_ROOT_API + "topicfile/",
                                data=data_json,
                                headers=headers)
            print(res.json())
            if res.json().get('result') == 8400:  # ChatServer가 제대로 websocket을 보내지 않은 경우
                return Response({'result': status_code['CHAT_MADE_FAIL']}, status=status.HTTP_200_OK)

            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopicFileDownloadView(APIView):
    # queryset = TopicFile.objects.all()
    serializer_class = TopicFileDownloadSerializer

    def get(self, *args, **kwargs):
        print("[[TopicFileDownloadView]] get")
        message_id = self.kwargs['message_id']  # data in url

        # message_id에 해당하는 TopicMessage의 TopicFile을 가져온다
        topic_message = TopicMessage.objects.get(pk=message_id)
        topic_file = TopicFile.objects.get(message=topic_message)
        topic_filename = topic_file.get_filename()  # 저장된 파일명 반환
        print("topic_filename: " + str(topic_filename))

        # 현재 프로젝트 최상위 (부모폴더) 밑에 있는 'topic_filename' 파일
        filepath = os.path.join(MEDIA_ROOT, topic_filename)
        print("filepath: " + str(filepath))
        origin_filename = topic_file.origin_filename  # 원래의 파일명 반환
        print("origin_filename: " + str(origin_filename))

        with open(filepath, 'rb') as f:
            response = HttpResponse(f, content_type='application/octet-stream')
            # 필요한 응답헤더 세팅
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(origin_filename)
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response


##############################################################################################

class ChatRoomFileUploadView(APIView):
    queryset = ChatRoomFile.objects.all()
    # parser_classes = (FileUploadParser,)
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ChatRoomFileUploadSerializer

    def post(self, request, format=None, *args, **kwargs):
        print("[[ChatRoomFileUploadView]] post")

        file = request.data['file']
        origin_filename = file.name

        user_id = request.data['user']
        user = User.objects.get(pk=user_id)

        chatroom_id = self.kwargs['chatroom_id']  # data in url
        chatroom = ChatRoom.objects.get(pk=chatroom_id)

        # ChatRoomessage 저장 & Serializer 형태로 변환
        chatroomMessage = ChatRoomMessage.objects.create(
            user=user,
            chatRoom=chatroom,
            contents=origin_filename,
            is_file=True)
        messages_serializer = ChatRoomMessageSerializer(chatroomMessage)

        # ChatRoomFile 저장
        request.data['message'] = chatroomMessage.id
        request.data['origin_filename'] = origin_filename
        file_serializer = ChatRoomFileUploadSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()

            # websocket으로 message send 하기 위해 필요한 정보를 ShevChatServer로 보낸다.
            send_data = {
                'room_id': chatroom_id,
                'username': user.user_name,
                'message': messages_serializer.data
            }
            data_json = json.dumps(send_data)
            # payload = {'json_payload': data_json}
            print(data_json)

            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

            res = requests.post("http://" + CHAT_SERVER + CHAT_SERVER_ROOT_API + "chatroomfile/",
                                data=data_json,
                                headers=headers)
            print(res.json())
            if res.json().get('result') == 8400:  # ChatServer가 제대로 websocket을 보내지 않은 경우
                return Response({'result': status_code['CHAT_MADE_FAIL']}, status=status.HTTP_200_OK)

            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatRoomFileDownloadView(APIView):
    # queryset = ChatRoomFile.objects.all()
    serializer_class = ChatRoomFileDownloadSerializer

    def get(self, *args, **kwargs):
        print("[[ChatRoomFileDownloadView]] get")
        message_id = self.kwargs['message_id']  # data in url

        # message_id에 해당하는 ChatRoomMessage의 ChatRoomFile을 가져온다
        chatroom_message = ChatRoomMessage.objects.get(pk=message_id)
        chatroom_file = ChatRoomFile.objects.get(message=chatroom_message)
        chatroom_filename = chatroom_file.get_filename()  # 저장된 파일명 반환
        print("chatroom_filename: " + str(chatroom_filename))

        # 현재 프로젝트 최상위 (부모폴더) 밑에 있는 'chatroom_filename' 파일
        filepath = os.path.join(MEDIA_ROOT, chatroom_filename)
        print("filepath: " + str(filepath))
        origin_filename = chatroom_file.origin_filename  # 원래의 파일명 반환
        print("origin_filename: " + str(origin_filename))

        with open(filepath, 'rb') as f:
            response = HttpResponse(f, content_type='application/octet-stream')
            # 필요한 응답헤더 세팅
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(origin_filename)
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response
