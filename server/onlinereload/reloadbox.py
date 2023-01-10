# -*- coding: utf-8 -*-

'''
命名取自mail box，都是一方送达后 另一方定时取出

该文件为手动热更入口文件，只需在MODULE_LIST中加入文件名即可
服务器会定时读取该文件内容，并将MODULE_LIST中的模块热更出去

模块名：  从根目录开始，中间用'.'隔开，不用以.py结尾，热更后在onlinereload的log中可以看到更新成功记录

注意：热更完记得清空MODULE_LIST，会有重复热更的危险（因为根据文件修改时间来判断）
'''

MODULE_LIST = []

# example: MODULE_LIST = ["script.gm.excutor",]