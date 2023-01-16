# encoding: utf-8
"""
@author: lin
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: 739217783@qq.com
@software: Pycharm
@file: tes.py
@time: 2022/6/9 19:47
@desc:
- 检索文件是否有Front-matter
- 检索Front-matter中标题名是否与文件名相同
- 修改任意属性和值
TODO:字段（标签）是否有#，有的去除
TODO:使用正则检测时间格式是否符合特定格式
"""
import os
import re
from functools import wraps


def rw_file(func):
    @wraps(func)
    def wrapper(*args, **kw):
        with open(file_path, 'r', encoding='utf-8') as r:
            # 使用正则，通过全文(字符串，r.read)，识别Front-matter 和 正文区域
            _regex = re.compile(r'([-]{3})(.*?)([-]{3})', re.S | re.M)
            result = _regex.search(r.read())
            r.seek(0)

            try:
                # 划分内容
                content = r.readlines()  # 获取全文(list)，用于划分
                yaml_row = len(result.group().split('\n'))  # YAML区域的行数
                yaml_content = content[0:yaml_row]  # Front-matter
                body = content[yaml_row:]  # 正文

                if func.__name__ == 'get_info':
                    # 如果是读取信息，直接返回信息
                    return func(yaml_content, body, *args, **kw)

            except AttributeError:
                print(f'{os.path.split(kw["path"])[1]},没有Front-matter')
                return None

            # 执行需要的操作
            w_content = func(yaml_content, body, *args, **kw)

        with open(file_path, 'w', encoding='utf-8') as w:
            w.write(w_content)

    return wrapper


@rw_file
def get_info(yaml_content: list, body: list):
    """
    获取信息
    @return:
    """
    return dict(yaml=yaml_content, body=body)


@rw_file
def edit_attr(yaml_content: list, body: list, attr_before: str = None, attr_after: str = None, replace_dict: dict = None) -> str:
    """修改属性名称
    @param yaml_content:Front-matter内容
    @param body:正文内容
    @param attr_before:需要修改的属性名称
    @param attr_after:修改后的属性名称
    允许单个替换或者多个替换(如果同时提供单个替换和多个替换，多个替换优先级高于单个替换)
    单个替换,提供attr_before和attr_after参数
    多个替换,仅提供replace_dict参数即可(键为要替换的属性名称，值为新属性名称)
    """

    if (attr_after == None and attr_before == None) and replace_dict == None:
        raise Exception("参数不能为空")
    elif attr_before == None:
        raise Exception("attr_before参数为空", "请提供需要修改的属性名称!")
    elif attr_after == None:
        raise Exception("attr_after参数为空", "请提供修改后的属性名称!")

    for index, value in enumerate(yaml_content):
        if replace_dict:
            # 有值，采用多个替换(根据提供的字典)
            for item in replace_dict.items():
                if value.find(item[0]) > -1 and value.find(':') > -1:
                    s_attr, s_value = value.split(':', 1)  # 获取属性名称和值
                    s_attr = s_attr.replace(item[0], item[1])
                    yaml_content[index] = s_attr + ':' + s_value
        else:
            # 采用单个替换
            if value.find(attr_before) > -1 and value.find(':') > -1:
                s_attr, s_value = value.split(':', 1)  # 获取属性名称和值
                s_attr = s_attr.replace(attr_before, attr_after)
                yaml_content[index] = s_attr + ':' + s_value

    yaml_content.extend(body)  # 重新组合成全文(yaml_content+body)
    return ''.join(yaml_content)  # 列表转回文本


@rw_file
def edit_value(yaml_content: list, body: list, attr: str, up_value: str):
    """修改属性值
    @param yaml_content:Front-matter内容
    @param body:正文内容
    @param attr:需要修改的属性名称
    @param up_value:对应属性需要修改的值
    @return:
    """
    for index, value in enumerate(yaml_content):
        if value.find(attr) > -1 and value.find(':') > -1:
            s_attr, s_value = value.split(':', 1)
            yaml_content[index] = s_attr + ':' + up_value + '\n'

    yaml_content.extend(body)  # 重新组合成全文(yaml_content+body)
    return ''.join(yaml_content)  # 列表转回文本


@rw_file
def delete_attr(yaml_content: list, body: list, attr: str):
    """删除指定属性
    @param yaml_content:Front-matter内容
    @param body:正文内容
    @param attr: 需要删除（移除）的attr
    @return:
    """
    for index, value in enumerate(yaml_content):
        if value.find(attr) > -1 and value.find(':') > -1:
            yaml_content.remove(value)

    yaml_content.extend(body)  # 重新组合成全文(yaml_content+body)
    return ''.join(yaml_content)  # 列表转回文本


@rw_file
def replce_shuangyin(yaml_content, body):
    """移除YAML区域双引号"""
    for index, value in enumerate(yaml_content):
        yaml_content[index] = value.replace('"', "")

    yaml_content.extend(body)  # 重新组合成全文(yaml_content+body)
    return ''.join(yaml_content)  # 列表转回文本


def sx(x):
    """
    判断指定路径在不在要跳过的列表中，在的话返回True，不在的话False
    @param x:
    @return:
    """
    ignore = [r'C:\0资源库\0_笔记库\.obsidian', r"C:\0资源库\0_笔记库\.stfolder", r"C:\0资源库\0_笔记库\.trash", r"C:\0资源库\0_笔记库\assets", r"C:\0资源库\0_笔记库\config",
              r"C:\0资源库\0_笔记库\config\Templates"]  # 要忽略，跳过的文件（例如工作区文件就肯定是没有Front-matter的）

    for i in ignore:
        if x.find(i) > -1:
            return True
    return False


if __name__ == '__main__':
    # for root, dirs, file in os.walk(r"C:\0系统库\桌面\新建文件夹 (3)"):
    #     if sx(root):
    #         continue
    #     for i in file:
    #         if i.endswith('.md'):
    #             file_path = root + '/' + i
    #             edit_attr()

    file_path = r"C:\0系统库\桌面\测试\解决Hexo图片无法显示问题.md"
    a = {"date created": "data", "name": "title"}
    # edit_attr(replace_dict=a)
    edit_attr()
    # edit_attr("name", "title")

    # print(get_info())    # print(get_info())
