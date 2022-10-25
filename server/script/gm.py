# -*- coding: utf-8 -*-

from script.common import S2CShowToast

import netpackage as np

def ExecGMOrder(sOpenID, oNetPackage):
    sOrder = np.UnpackS(oNetPackage)
    PrintDebug(sOrder)
    exec(sOrder)

    S2CShowToast(sOpenID, "", "success", "GM执行成功")