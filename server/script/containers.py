# -*- coding: utf-8 -*-

if "g_ListContainer" not in globals():
    g_ListContainer = []

def Regist(oContainer):
    global g_ListContainer
    g_ListContainer.append(oContainer)

def Init():
    return

class CListContainer(list):
    def Save(self):
        data = []
        for obj in self:
            data.append(obj.Save())
        self.clear()
        return data