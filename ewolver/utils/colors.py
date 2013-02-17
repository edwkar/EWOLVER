# vim: ts=4:sw=4


_new_colorizer = lambda c: lambda x: '\033['+str(c)+'m'+str(x)+'\033[0m'
BLUE, GREEN, YELLOW = map(_new_colorizer, [94, 92, 93])
