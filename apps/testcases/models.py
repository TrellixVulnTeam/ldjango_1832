from django.db import models

# Create your models here.
from django.db import models
from utils.base_models import BaseModel


class Testcases(BaseModel):
    id = models.AutoField(verbose_name='ID主键', primary_key=True, help_text='ID主键')
    name = models.CharField(verbose_name='用例名称', max_length=200, unique=True, help_text='用例名称')
    interface = models.ForeignKey('interfaces.Interfaces', on_delete=models.CASCADE,
                                  related_name='testcases', help_text='所属接口')
    include = models.TextField(verbose_name='前置条件', null=True, help_text='用例执行前置顺序')
    author = models.CharField(verbose_name='编写人员', max_length=50, help_text='编写人员')
    request = models.TextField(verbose_name='请求信息', help_text='请求信息')

    class Meta:
        db_table = 'db_testcases'
        verbose_name = '测试用例'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


