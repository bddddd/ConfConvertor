import json
import xml.dom.minidom
import xml.etree.ElementTree as ET

import requests
from flask import Request, make_response, request

from Clash.ToClash import ToClash
from Clash.TopologicalSort import TopologicalSort
from Emoji.emoji import EmojiParm, EmojiType, SSEmoji, SSREmoji, SurgeListEmoji
from Expand.ExpandPolicyPath import ExpandPolicyPath
from Expand.ExpandRuleSet import ExpandRuleSet
from Filter.filter import SrugeListFilter, SSFilter, SSRFilter, SurgeConfFilter
from Surge3.ToSurge3 import ToSurge3
from Unite.CheckPolicyPath import NeedExpandPolicyPath
from Unite.GetProxyGroupType import GetProxyGroupType
from Unite.Surge3LikeConfig2XML import Content2XML


def Surge3(request):
    """
    Args:
        request (flask.Request): HTTP request object.
    Return:
        A Surge3Pro-support configuration
    Do:
        Get 2 parameters: url & filename
        url: the url of the remote file
        filename: the file name of the configuration will be returned, default(no filename parameter in request) to Config.conf

        Function ExpandPolicyPath will be excuted only when 'Proxy Group' illegal format be exist
        Illegal format: a 'Proxy Group' only allow one policy when there is a policy-path
    """
    url = request.args.get('url')
    filename = request.args.get("filename", "Config.conf")
    interval = request.args.get("interval", "86400")
    strict = request.args.get("strict", "false")
    content = requests.get(url).text
    result = "#!MANAGED-CONFIG https://api.OKAB3.com/surge3?url=" + url + \
        "&filename="+filename+"&interval="+interval+"&strict=" + \
        strict + " interval="+interval+" strict="+strict+"\n"
    x = Content2XML(content)
    x = ExpandPolicyPath(x)
    x = GetProxyGroupType(x)

    result += ToSurge3(x)

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename="+filename
    return response


def Clash(request):
    url = request.args.get('url')
    filename = request.args.get("filename", "Config.yml")
    snippet = request.args.get("snippet")
    url_text = requests.get(url).content.decode()
    x = Content2XML(url_text)
    x = ExpandPolicyPath(x)
    x = ExpandRuleSet(x)
    x = TopologicalSort(x)

    result = ToClash(x, snippet)

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename="+filename
    return response


def Filter(request):
    filter_type = str(request.args.get("type"))
    filter_type_lower = filter_type.lower()
    if filter_type_lower == "surgelist":
        return SrugeListFilter(request).filter_source()
    elif filter_type_lower == "surgeconf":
        return SurgeConfFilter(request).filter_source()
    elif filter_type_lower == "ss":
        return SSFilter(request).filter_source()
    elif filter_type_lower == "ssr":
        return SSRFilter(request).filter_source()
    else:
        return "Illegal value for parameter type: "+filter_type+". Please see https://github.com/0KABE/ConfConvertor for details"


def Emoji(request: Request):
    source_type: EmojiType = EmojiType(request.args.get(EmojiParm.TYPE.value))
    if source_type == EmojiType.SURGE_LIST:
        return SurgeListEmoji(request).convert()
    elif source_type == EmojiType.SS:
        return SSEmoji(request).convert()
    elif source_type == EmojiType.SSR:
        return SSREmoji(request).convert()
