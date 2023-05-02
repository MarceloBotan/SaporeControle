from django import template

register = template.Library()

def qs_range_len(value):
    return range(int(len(value)))

def getIndex(value, i):
    return value[i]

register.filter("qs_range_len", qs_range_len)
register.filter("getIndex", getIndex)