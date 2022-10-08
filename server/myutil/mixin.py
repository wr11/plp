# -*- coding: utf-8 -*-

import types

def MixinMergeClass(Class, MixinClass, bMakeLast = True, bReplaceAttr = True):
	attrList = dir(Class)
	if not MixinClass in Class.__bases__:
		if bMakeLast:
			Class.__bases__ = Class.__bases__ + (MixinClass, )
		else:
			Class.__bases__ = (MixinClass, ) + Class.__bases__
	if not bReplaceAttr:
		return
	for attr in dir(MixinClass):
		if attr.startswith("__"):
			continue
		if attr in attrList:
			PrintWarning("warning: %s.%s already exists" % (MixinClass.__name__, attr))
		oAttr = getattr(MixinClass, attr)
		if type(oAttr) is types.MethodType:
			oAttr = oAttr.im_func
		setattr(Class, attr, oAttr)
	return Class

def MixinGloabalFunc(Class, lstFunc):
	attrList = dir(Class)
	for func in lstFunc:
		sFunc = func.__name__
		if sFunc in attrList:
			PrintWarning("warning: %s.%s already exists" % (Class.__name__, sFunc))
		setattr(Class, sFunc, types.MethodType(func, Class))
	return Class