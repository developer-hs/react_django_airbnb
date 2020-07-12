from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room
from .serializers import ReadRoomSerializer, WriteRoomSerializer


@api_view(["GET", "POST"])
def rooms_view(request):
    if request.method == "GET":
        rooms = Room.objects.all()
        serializer = ReadRoomSerializer(rooms, many=True).data
        return Response(serializer)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = WriteRoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(user=request.user)
            room_serializer = ReadRoomSerializer(room).data
            return Response(data=room_serializer, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ↑ Same ↓


class RoomsView(APIView):

    def get(self, request):
        rooms = Room.objects.all()
        serializer = ReadRoomSerializer(rooms, many=True).data
        # many = True : 많은 항목들을 표시해야 할 경우 many = True 설정을 해줘야한다
        return Response(serializer)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = WriteRoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(user=request.user)
            room_serializer = ReadRoomSerializer(room).data
            return Response(data=room_serializer, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SeeRoomView(RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = ReadRoomSerializer

# ↑ Same ↓


class RoomView(APIView):

    def get_room(self, pk):
        try:
            room = Room.objects.get(pk=pk)
            return room
        except Room.DoesNotExist:
            return None

    def get(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            serilalizer = ReadRoomSerializer(room).data
            return Response(data=serilalizer, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            if room.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serilalizer = WriteRoomSerializer(
                room, data=request.data, partial=True)
            # update 를 하기위해선 instance 가 필요하다 ,
            # instance 가 없다면 serializer 는 create() 를 호출

            # partial = True : serializer 에게 모든 필수 fields 에 대한
            # 값들을 pass 시켜주고 내가 바꾸고싶은 데이터만 보내게 해줌
            if serilalizer.is_valid():
                room = serilalizer.save()  # serializers.py → validate → update
                serilalizer_room = ReadRoomSerializer(room).data
                return Response(data=serilalizer_room)
            else:
                return Response(data=serilalizer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            if room.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            room.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
