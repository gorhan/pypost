from time import localtime, strftime
from sys import stderr, stdout
from inspect import stack


class Logs:
    WARN='WARN'
    ERROR='ERROR'
    INFO='INFO'
    @classmethod
    def LOG2FP(cls, log):
        if log == Logs.WARN or log == Logs.INFO:
            return stdout
        elif log == Logs.ERROR:
            return stderr


def LOG(**kwargs):
    stck = stack()[1][0]
    # print stck.f_locals
    caller_class = stck.f_locals['cls'].__name__ if 'cls' in stck.f_locals else stck.f_locals['self'].__class__.__name__
    caller_func = stck.f_code.co_name

    if not kwargs.has_key('log'):
        kwargs['log'] = Logs.INFO

    log = '%s From %50s %5s: %s' % (
        strftime('[%d-%m-%Y - %H:%M:%S]', localtime()),
        caller_class + '.' + caller_func,
        kwargs['log'],
        kwargs['msg']
    )

    out = kwargs['fp'] if kwargs.has_key('fp') else Logs.LOG2FP(kwargs['log'])
    if not kwargs.has_key('n_print'):
        print >>out, log
        out.flush()

    return log