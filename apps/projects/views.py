from rest_framework import viewsets, status

from rest_framework import permissions
from rest_framework.response import Response

from projects.models import Projects
from interfaces.models import Interfaces
from projects.serializer import ProjectModeSerializer, ProjectNameSerializer, ProjectsRunSerializer
from rest_framework.decorators import action

from projects.utils import get_count_by_project
# from utils import common
from datetime import datetime
import os
from django.conf import settings
from envs.models import Envs
from testcases.models import Testcases
from utils import common


class ProjectsViewSet(viewsets.ModelViewSet):
    """
    	list:
    	获取项目列表数据

    	create:
    	创建项目

    	destroy:
    	删除项目

    	update:
    	完整更新项目

    	partial_update:
    	部分更新项目

    	retrieve:
    	获取项目详情数据

    	names:
    	获取所有项目ID和项目名

    	interfaces:
    	获取某个项目下的所有接口信息

    	"""
    queryset = Projects.objects.filter(is_delete=False)
    serializer_class = ProjectModeSerializer
    # 指定过滤引擎
    # filter_fields = [DjangoFilterBackend]
    filter_fields = ['id', 'name', 'tester']
    # 指定权限类
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()  # 逻辑删除

    # 可以是用action装饰器声明自定义的动作
    # detail(url是否需要传递Pk，一条数据为True)
    @action(methods=['get'], detail=False)
    def names(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ProjectNameSerializer(instance=queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def interfaces(self, request, pk=None):
        interface_objs = Interfaces.objects.filter(project_id=pk, is_delete=False)
        one_list = []
        for obj in interface_objs:
            one_list.append({
                'id': obj.id,
                'name': obj.name
            })
        return Response(data=one_list)

    def list(self, request, *args, **kwargs):
        # queryset = self.filter_queryset(self.get_queryset())
        #
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     datas = serializer.data
        #     datas = get_count_by_project(datas)
        #     return self.get_paginated_response(datas)
        #
        # serializer = self.get_serializer(queryset, many=True)
        # datas = serializer.data
        # datas = get_count_by_project(datas)
        # return Response(datas)

        response = super().list(request, *args, **kwargs)
        response.data['results'] = get_count_by_project(response.data['results'])
        return response

    # @action(methods=['post'], detail=True)
    # def run(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data)
    #     serializer.is_valid()
    #     datas = serializer.validated_data
    #
    #     env_id = datas.get('env_id')
    #     testcase_dir_path = os.path.join(settings.SUITES_DIR, datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f'))
    #     if not os.path.exists(testcase_dir_path):
    #         os.mkdir(testcase_dir_path)
    #
    #     # first()返回queryset查询集第一项
    #     env = Envs.objects.filter(id=env_id, is_delete=False).first()
    #     # 项目下所有接口
    #     interface_objs = Interfaces.objects.filter(is_delete=False, project=instance)
    #
    #     if not interface_objs.exists():
    #         data_dict = {
    #             'detail': '此项目下没有接口，无法运行'
    #         }
    #         return Response(data_dict, status=status.HTTP_400_BAD_REQUEST)
    #
    #     for inter_obj in interface_objs:
    #         testcase_objs = Testcases.objects.filter(is_delete=False, interface=inter_obj)
    #
    #         for one_obj in testcase_objs:
    #             # 生成yml文件
    #             common.generate_testcase_files(one_obj, env, testcase_dir_path)
    #
    #     # 运行用例
    #     return common.run_testcase(instance, testcase_dir_path)

    def get_serializer_class(self):
        if self.action == 'names':
            return ProjectNameSerializer
        elif self.action == 'run':
            return ProjectsRunSerializer
        else:
            return self.serializer_class

    @action(methods=['post'], detail=True)
    def run(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        datas = serializer.validated_data
        env_id = datas.get('env_id')

        #创建测试用例所在目录名
        testcase_dir_path = os.path.join(settings.SUITES_DIR, datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f'))

        if not os.path.exists(testcase_dir_path):
            os.mkdir(testcase_dir_path)

        env = Envs.objects.filter(id=env_id, is_delete=False).first()
        interface_objs = Interfaces.objects.filter(is_delete=False, project=instance)

        if not interface_objs.exists():
            data_dict = {
                'detail': '此项目下无接口，无法运行'
            }
            return Response(data_dict, status=status.HTTP_400_BAD_REQUEST)

        for inter_obj in interface_objs:
            testcase_objs = Testcases.objects.filter(is_delete=False, interface=interface_objs)

            for one_obj in testcase_objs:
                common.generate_testcase_files(one_obj,env,testcase_dir_path)

        return common.run_testcase(instance, testcase_dir_path)