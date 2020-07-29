from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .models import Room
from .serializers import RoomSerializer


class OwnPagination(PageNumberPagination):
    page_size = 20


@api_view(["GET", "POST"])
def rooms_view(request):
    if request.method == "GET":
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True).data
        return Response(serializer)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(user=request.user)
            room_serializer = RoomSerializer(room).data
            return Response(data=room_serializer, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ↑ Same ↓


class RoomsView(APIView):

    def get(self, request):
        paginator = OwnPagination()
        #               ↑
        # paginator = PageNumberPagination()
        # paginator.page_size = 20 과 같다
        rooms = Room.objects.all()
        results = paginator.paginate_queryset(rooms, request)
        # request 를 파싱하는 이유는 page query argument 를 찾기위해서이다
        serializer = RoomSerializer(results, many=True, context={
                                    "request": request}).data
        # many = True : 많은 항목들을 표시해야 할 경우 many = True 설정을 해줘야한다
        # context : 해당 Serializer 에 객체(context)를 넘겨줌
        return paginator.get_paginated_response(serializer)
        # paginator.get_paginated_response() 를 사용 하게되면
        # paginator 일 경우 count,next,previous 를 사용할 수 있음

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(user=request.user)
            room_serializer = RoomSerializer(room).data
            return Response(data=room_serializer, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SeeRoomView(RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

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
            serilalizer = RoomSerializer(room).data
            return Response(data=serilalizer, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            if room.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serilalizer = RoomSerializer(
                room, data=request.data, partial=True)
            # 첫번째 인자는 instance 이다
            # update 를 하기위해선 instance 가 필요하다 ,
            # instance 가 없다면 serializer 는 create() 를 호출

            # partial = True : serializer 에게 모든 필수 fields 에 대한
            # 값들을 pass 시켜주고 내가 바꾸고싶은 데이터만 보내게 해줌
            if serilalizer.is_valid():
                room = serilalizer.save()  # serializers.py → validate → update
                serilalizer_room = RoomSerializer(room).data
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


@api_view(["GET"])
def room_serach(request):
    max_price = request.GET.get("max_price", None)
    min_price = request.GET.get("min_price", None)
    beds = request.GET.get("beds", None)
    bedrooms = request.GET.get("bedrooms", None)
    bathrooms = request.GET.get("bathrooms", None)
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)
    filter_kwargs = {}
    if max_price is not None:
        filter_kwargs["price__lte"] = max_price
    if min_price is not None:
        filter_kwargs["price__gte"] = min_price
    if beds is not None:
        filter_kwargs["beds__gte"] = beds
    if bedrooms is not None:
        filter_kwargs["bedrooms__gte"] = bedrooms
    if bathrooms is not None:
        filter_kwargs["bathrooms__gte"] = bathrooms
    paginator = PageNumberPagination()
    paginator.page_size = 10
    if lat is not None and lng is not None:
        filter_kwargs["lat__gte"] = float(lat) - 0.005
        filter_kwargs["lat__lte"] = float(lat) + 0.005
        filter_kwargs["lng__gte"] = float(lng) - 0.005
        filter_kwargs["lng__lte"] = float(lng) + 0.005
    try:
        rooms = Room.objects.filter(**filter_kwargs)
        # **filter_kwargs(unpacking) :
        # * 을 할경우 dict 의 모든 key 값을 반환한다
        # ** 을 할 경우 key = "value" 값으로 반환해준다
    except ValueError:
        rooms = Room.objects.all()
    results = paginator.paginate_queryset(rooms, request)
    serializer = RoomSerializer(results, many=True).data
    return paginator.get_paginated_response(serializer)
    # paginator.get_paginated_response() 를 사용 하게되면
    # paginator 일 경우 count,next,previous 를 사용할 수 있음
