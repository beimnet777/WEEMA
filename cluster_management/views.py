from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Cluster, SelfHelpGroup, Member
from .serializers import ClusterSerializer, SelfHelpGroupSerializer, MemberSerializer


# Cluster ViewSet
class ClusterViewSet(ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'location', 'cluster_manager']
    search_fields = ['cluster_name', 'location']
    ordering_fields = ['cluster_name', 'total_groups', 'created_at', 'updated_at']


# Self Help Group ViewSet
class SelfHelpGroupViewSet(ModelViewSet):
    queryset = SelfHelpGroup.objects.all()
    serializer_class = SelfHelpGroupSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'location', 'cluster', 'group_leader']
    search_fields = ['group_name', 'location']
    ordering_fields = ['group_name', 'total_members', 'created_at', 'updated_at']


# Member ViewSet
class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'gender',
        'age',
        'marital_status',
        'religion',
        'is_other_shg_member_in_house',
        'is_responsible_for_children',
        'group'
    ]
    search_fields = ['first_name', 'last_name', 'name']
    ordering_fields = ['age', 'hh_size', 'created_at', 'updated_at']