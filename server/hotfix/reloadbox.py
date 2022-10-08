# -*- coding: utf-8 -*-

'''
命名取自mail box，都是一方送达后 另一方定时取出

该文件为手动热更入口文件，只需在FILE_LIST中加入文件名即可
服务器会定时读取该文件内容，并将FILE_LIST中的模块热更出去

文件名example: "hotfix.reloadbox"  从根目录开始，中间用'.'隔开

注意：热更完记得清空FILE_LIST，如果热更密集，可以等所有热更更完后再清空
'''

FILE_LIST = []