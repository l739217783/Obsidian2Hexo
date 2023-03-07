# encoding: utf-8
"""
@author: lin
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: 739217783@qq.com
@software: Pycharm
@file: Ob2Hexo.py
@time: 2023/1/14 23:31
@desc:
传入指定文件名，将对应Ob库下的md文件复制一份到Hexo目录下
修改Front-matter成Hexo需要的格式
"""
import os
import re
import shutil
import sys
import Front_matter_edit as fm
import json
from time import sleep


class Ob2Hexo():
    def __init__(self, file_name: str = None) -> None:
        # yapf:disable
        try:
            self.file_name = file_name
            with open("D:\develop\Python\Quicker\Obsidian2Hexo\setting.json", encoding='utf-8') as f:
                setting = json.load(f)
                self.ob_path = setting["ob_path"]                  # OB库的位置
                self.photo_path = setting["photo_path"]            # OB图片位置
                self.hexo_path = setting["hexo_path"]              # Hexo文章位置
                self.hexo_photo_path = setting["hexo_photo_path"]  # Hexo图片位置
                self.rep_dict = setting["rep_dict"]                # 替换的属性
                self.del_list = setting["del_list"]                # 删除的属性
                # 同步标签，用于存量同步
                self.sync_tags = setting["sync_tags"]
                # 别名检测,默认true
                self.aliases_check = setting["aliases_check"]
                # 是否移除同步标签,默认true
                self.syncTags_rpl = setting["syncTags_rep"]
                self.hexo_file_path = os.path.join(
                    self.hexo_path, self.file_name + '.md') if file_name else None
                # Hexo文章存放文件路径,可能采用存量同步(tag_sync,update_sync),默认None
            if not os.path.exists("D:\develop\Python\Quicker\Obsidian2Hexo\Front_matter_edit.py"):
                raise Exception('依赖文件确缺失')
        except FileNotFoundError:
            raise Exception("配置文件缺失")

    def replace(self, file, old_content, new_content):
        """给定文件路径,将旧内容替换为新内容
        Args:
            file (str): 文件路径
            old_content (str): 旧内容
            new_content (str): 新内容
        """
        content = self.read_file(file)
        content = content.replace(old_content, new_content)
        self.write_file(file, content)

    def read_file(self, file_path, mode='read'):
        """读文件内容
        Args:
            file_path (str): 文件路径
            mode(str):read、readline
        Returns:
            str: 文件内容
        """
        with open(file_path, 'r', encoding='UTF-8') as f:
            if mode == 'read':
                read_all = f.read()
            else:
                read_all = f.readlines()
            f.close()

        return read_all

    def write_file(self, file_path, data):
        """写内容到文件
        Args:
            file_path (str): 文件路径
            data (str): 文件内容
        """
        with open(file_path, 'w', encoding='UTF-8') as f:
            f.write(data)
            f.close()

    def adn2note(self, file_path):
        """callout转便签"""
        adn = re.compile(r"\>\s*\[!.+\]\-?(.+)?")  # 笔记块 + 折叠块
        black = re.compile(r'^\s$')
        quote = re.compile(r'>\s*.+')
        null_quote = re.compile(r'>\s*\n')
        content = self.read_file(file_path, 'readline')
        switch = False
        tag = ['note', 'info', 'danger', 'warning']

        for index, value in enumerate(content):
            if value.find('>') > -1 and adn.search(value):
                # 检测到笔记块类型
                # 获取标题
                title = value.replace('>[!', '').replace('> [!', '').replace(
                    ']', '').replace(']-', '').replace('-', '').strip()
                for tag_index, tag_value in enumerate(tag):
                    if title.find(tag_value) > -1:
                        # 移除原有标签(note、info、danger、warning)
                        title = title.replace(tag_value, "").strip()
                        # 如果标题仅有callout，例如：>[!note]，那么不增加标题信息，有的话增加一行标题信息
                        content[index] = "{% note " + tag_value + " %}\n" if title == '' else "{% note " + \
                            tag_value + " %}\n" + f"{title}\n"  # yapf:disable
                        break
                    elif title.find(tag_value) == -1 and tag_index == (len(tag) - 1):
                        # 如果是采用自拟标题：>[!笔记二]-，并且没有找任意支持标签，默认采用note light标签
                        content[index] = "{% note light %}\n" + f"{title}\n"
                switch = True
            elif switch and quote.search(value):
                content[index] = value.replace('>', '').strip() + '\n'
            elif switch and null_quote.search(value):
                content[index] = '\n'
            elif switch and black.search(value):
                content[index] = '{% endnote %}\n\n'
                switch = False

            if index + 1 == len(content) and quote.search(value):
                # 如果最后是引用,没有空行可以转换收尾标签,多添加一行收尾标签
                content.append('{% endnote %}\n\n')

        content = ''.join(content)
        self.write_file(file_path, content)

    def get_photo(self, file_path):
        """将md文件中的所有图片复制到Hexo目录下
        Args:
            file_path (str): 文件路径(Hexo的md文件路径)
        """
        content = self.read_file(file_path)
        pattern = re.compile(r'(?:!\[(.*?)\]\((.*?)\))', re.M)

        result = pattern.findall(content)

        # 获取md文档中的所有图片链接,修改图片路径成相对路径
        for photo in result:
            photo_name = os.path.split(photo[1])[1]  # 无转码的无路径图片名
            if photo_name.find('.') == -1:
                # 图片名没有.的跳过，有可能是说明：`![]()` 或者其他特殊情况
                continue
            r_photo_name = photo_name.replace(
                '%20', ' ')  # 移除空格，编码转换回空格(复制图片使用)
            # print(photo, photo_name, r_photo_name)
            shutil.copyfile(os.path.join(self.photo_path, r_photo_name), os.path.join(
                self.hexo_photo_path, r_photo_name))
            content = content.replace(
                photo[1], f"{os.path.join('../images/',photo_name)}")

        self.write_file(file_path, content)

    def tags_sync(self, rpl_switch: bool = False):
        """对包含指定标签的文件全部更新到Hexo
        注意：会进行覆写操作，不会提示
        Args:
            rpl_switch (bool): 是否移除公开标签
        """

        for root, dirs, files in os.walk(self.ob_path):
            for file in files:
                if file.endswith('.md'):
                    fm.file_path = os.path.join(root, file)
                    tag_list = fm.get_tags()
                    if self.sync_tags in tag_list:
                        print(f'更新文章：{file}')
                        hexo_file_path = os.path.join(self.hexo_path, file)
                        shutil.copyfile(os.path.join(
                            root, file), hexo_file_path)

                        # front-matter转换
                        fm.file_path = hexo_file_path
                        if self.del_list:
                            for del_str in self.del_list:
                                fm.delete_attr(del_str)  # 删除不需要属性

                        if rpl_switch:
                            fm.file_path = hexo_file_path
                            fm.delete_value(
                                del_dict=['tags', self.sync_tags])  # 删除公开标签

                        if self.rep_dict:
                            fm.edit_attr(replace_dict=self.rep_dict)  # 替换标签

                        self.adn2note(hexo_file_path)  # callout 转换
                        self.get_photo(hexo_file_path)  # 复制图片到Hexo目录下

    def update_sync(self):
        """更新同步
        对Hexo现有的文件全部更新(从Obsidian拉取)
        注意：会进行覆盖操作，不会提示
        """
        Hexo_file_list = [i for i in os.listdir(
            self.hexo_path) if i.endswith('.md')]

        for root, dirs, files in os.walk(self.ob_path):
            for file in files:
                if file in Hexo_file_list:
                    hexo_file_path = os.path.join(self.hexo_path, file)
                    shutil.copyfile(os.path.join(root, file), hexo_file_path)

                    # front-matter转换
                    fm.file_path = hexo_file_path
                    if self.del_list:
                        for del_str in self.del_list:
                            fm.delete_attr(del_str)  # 删除不需要属性

                    if self.rep_dict:
                        fm.edit_attr(replace_dict=self.rep_dict)  # 替换标签

                    self.adn2note(hexo_file_path)  # callout 转换
                    self.get_photo(hexo_file_path)  # 复制图片到Hexo目录下

    def main(self):
        """给定文件名，拷贝文件(md、相关图片)到hexo目录下,Quicker使用
        Args:
            file_name (str): 文件名
        """
        title = re.compile(f'^{self.file_name}$')

        # 复制文件
        for root, dirs, files in os.walk(self.ob_path):
            for file in files:
                result = title.search(os.path.splitext(file)[0])
                if result:
                    if os.path.exists(self.hexo_file_path):
                        while (True):
                            answer = input('文件已存在，是否覆盖文件(yes/no)?')
                            if answer == 'yes':
                                break
                            elif answer == 'no':
                                sys.exit(0)
                            os.system("cls")
                            continue
                    shutil.copyfile(os.path.join(root, file),
                                    self.hexo_file_path)
                    break  # 找到文件直接退出遍历
            else:
                continue
            break

        # front-matter和正文的处理
        fm.file_path = self.hexo_file_path
        if self.aliases_check:
            ali_list = []
            yaml_dict = fm.yaml_list2dict()
            print(yaml_dict.keys())

            if 'aliases' in yaml_dict.keys():
                # 不管是否数组,转换为数组,方便后续选择
                if type(yaml_dict['aliases']) == str:
                    ali_list.append(yaml_dict['aliases'])
                else:
                    ali_list.extend(yaml_dict['aliases'])

                while True:
                    print('=' * 20)
                    for index, value in enumerate(ali_list):
                        print(f"{index + 1}:{value}\n")
                    print('=' * 20, '\n')

                    answer = input('是否采用别名的话(序号/No)?')
                    if answer.isdigit() and int(answer) <= len(ali_list):
                        rpl_title = ali_list[int(answer) - 1]
                        fm.edit_value(attr='name', after_value=rpl_title)
                    elif answer.lower() == 'no':
                        print('采用原标题')
                        sleep(3)
                    else:
                        print('请输入正确选项！')
                        sleep(3)
                        os.system("cls")
                        continue
                    break

        if (self.syncTags_rpl) and (self.syncTags_rpl in yaml_dict.keys()):
            # 移除公有标签，有的情况下)
            fm.delete_value(["tags", f"{self.sync_tags}"])

        if self.del_list:
            # 删除指定属性
            for del_str in self.del_list:
                fm.delete_attr(del_str)

        if self.rep_dict:
            # 替换指定属性
            fm.edit_attr(replace_dict=self.rep_dict)

        self.adn2note(self.hexo_file_path)  # callout 转换
        self.get_photo(self.hexo_file_path)  # 资源拷贝(图片)

        sys.exit(0)


if __name__ == '__main__':
    # file_name = sys.argv[1]
    file_name = r"实践_日历"  # 测试使用
    # h_file_name = r"C:\Hexo\source\_posts\图片路径测试.md"  # 测试使用
    # print(file_name)
    ob2hexo = Ob2Hexo(file_name)
    ob2hexo.main()
    # print(ob2hexo.file_name)
    # print(ob2hexo.aliases_check)
    # ob2hexo = Ob2Hexo()
    # ob2hexo.tags_sync(True)
