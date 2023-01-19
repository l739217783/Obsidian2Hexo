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


class Ob2Hexo():
    def __init__(self, file_name: str = None) -> None:
        try:
            self.file_name = file_name  # 单文件名,无后缀
            with open("setting.json", encoding='utf-8') as f:
                # 获取配置信息
                setting = json.load(f)
                self.ob_path = setting["ob_path"]  # OB库的位置
                self.photo_path = setting["photo_path"]  # OB库附件存放位置
                self.hexo_path = setting["hexo_path"]  # Hexo存放文章的位置
                self.hexo_photo_path = setting["hexo_photo_path"]  # Hexo存放图片的位置
                self.rep_dict = setting["rep_dict"]  # 需要替换的Front-matter属性名称
                self.del_list = setting["del_list"]  # 需要删除的Front-matter属性名称
                self.sync_tags = setting["sync_tags"]  # 同步标签，用于存量同步
                self.hexo_file_path = os.path.join(self.hexo_path, self.file_name + '.md') if file_name else None  # Hexo文章存放文件路径
                # 如果没有传入文件名,可能采用存量同步(tag_sync,update_sync),设置为None
            if not os.path.exists("Front_matter_edit.py"):
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
        # adn = re.compile(r'[>\s*[!].+\]')  # 笔记块类型
        # adn_fold = re.compile(r'[>\s*[!].+\]-')  # 折叠块类型
        adn = re.compile(r"\>\s*\[!.+\]\-?(.+)?")  # 匹配笔记块 + 折叠块
        black = re.compile(r'^\s$')
        quote = re.compile(r'>\s*.+')
        content = self.read_file(file_path, 'readline')
        switch = False
        tag = ['note', 'info', 'danger', 'warning']

        for index, value in enumerate(content):
            if value.find('>') > -1 and adn.search(value):
                # 检测到笔记块类型
                # 获取标题
                title = value.replace('>[!', '').replace('> [!', '').replace(']', '').replace(']-', '').replace('-', '').strip()
                for tag_index, tag_value in enumerate(tag):
                    if title.find(tag_value) > -1:
                        title = title.replace(tag_value, "").strip()  # 移除原有标签(note、info、danger、warning)
                        # 如果标题仅有callout，例如：>[!note]，那么不增加标题信息，有的话增加一行标题信息
                        content[index] = "{% note " + tag_value + " %}\n" if title == '' else "{% note " + tag_value + " %}\n" + f"{title}\n"  # yapf:disable
                        break
                    elif title.find(tag_value) == -1 and tag_index == (len(tag) - 1):
                        # 如果是采用自拟标题：>[!笔记二]-，并且没有找任意支持标签，默认采用note light标签
                        content[index] = "{% note light %}\n" + f"{title}\n"
                switch = True
            elif switch and quote.search(value):
                content[index] = value.replace('>', '').strip() + '\n'
            elif switch and black.search(value):
                content[index] = '{% endnote %}\n\n'
                switch = False

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
            r_photo_name = photo_name.replace('%20', ' ')  # 移除空格，编码转换回空格(复制图片使用)
            # print(photo, photo_name, r_photo_name)
            shutil.copyfile(os.path.join(self.photo_path, r_photo_name), os.path.join(self.hexo_photo_path, r_photo_name))
            content = content.replace(photo[1], f"{os.path.join('../images/',photo_name)}")

        self.write_file(file_path, content)

    def tags_sync(self, rpl_switch: bool = False):
        """对包含指定标签的文件全部更新到Hexo
        注意：会进行覆盖操作，不会提示
        Args:
            rpl_switch (_type_): Hexo是否移除Obsidian的公开标签(只用于知道是否同步Hexo,所以Hexo没必要有这个标签)
        """

        for root, dirs, files in os.walk(self.ob_path):
            for file in files:
                fm.file_path = os.path.join(root, file)
                tag_list = fm.get_tags()
                if self.sync_tags in tag_list:
                    hexo_file_path = os.path.join(self.hexo_path, file)
                    shutil.copyfile(os.path.join(root, file), hexo_file_path)

                    # front-matter转换
                    fm.file_path = hexo_file_path
                    if self.del_list:
                        for del_str in self.del_list:
                            fm.delete_attr(del_str)  # 删除不需要属性

                    if rpl_switch:
                        fm.file_path = hexo_file_path
                        fm.delete_value(del_dict=['tags', self.sync_tags])  # 删除公开标签

                    if self.rep_dict:
                        fm.edit_attr(replace_dict=self.rep_dict)  # 替换标签

                    self.adn2note(hexo_file_path)  # callout 转换
                    self.get_photo(hexo_file_path)  # 复制图片到Hexo目录下

    def update_sync(self):
        """更新同步
        对Hexo现有的文件全部更新(从Obsidian拉取)
        注意：会进行覆盖操作，不会提示
        """
        Hexo_file_list = [i for i in os.listdir(self.hexo_path) if i.endswith('.md')]

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
        """给定文件名，拷贝文件(md、相关图片)到hexo目录下
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
                    shutil.copyfile(os.path.join(root, file), self.hexo_file_path)
                    break  # 找到文件直接退出遍历
            else:
                continue
            break

        # front-matter转换
        fm.file_path = self.hexo_file_path

        if self.del_list:
            for del_str in self.del_list:
                fm.delete_attr(del_str)

        if self.rep_dict:
            fm.edit_attr(replace_dict=self.rep_dict)

        # callout 转换
        self.adn2note(self.hexo_file_path)

        # 复制图片到Hexo目录下
        self.get_photo(self.hexo_file_path)
        sys.exit(0)


if __name__ == '__main__':
    file_name = sys.argv[1]
    # file_name = r"2023.01.18 204040"  # 测试使用
    # h_file_name = r"C:\Hexo\source\_posts\图片路径测试.md"  # 测试使用
    # print(file_name)
    ob2hexo = Ob2Hexo(file_name)
    ob2hexo.main()
