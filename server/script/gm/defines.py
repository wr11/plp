# -*- coding: utf-8 -*-

#GM权限用户openid(仅限开发人员)，增加时请按照下面示例填写
AUTH_OPENID = [
    "o79YJ5C8MzIMv3YHvqbt0ysmmwTI",     #程序   魏骅玮
    "o79YJ5HU1u8i89k5GqZxgxVhSHXk",     #程序   范济海
]

def IsAuth(sOpenID):
    return sOpenID in AUTH_OPENID