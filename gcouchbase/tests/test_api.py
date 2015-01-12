from couchbase.tests.base import ApiImplementationMixin, SkipTest
try:
    import gevent
except ImportError as e:
    raise SkipTest(e)

from gcouchbase.bucket import Bucket, GView
from couchbase.tests.importer import get_configured_classes


class GEventImplMixin(ApiImplementationMixin):
    factory = Bucket
    viewfactor = GView
    should_check_refcount = True

    def _implDtorHook(self):
        import gc
        if not self.cb.closed:
            waiter = self.cb._get_close_future()
            del self.cb
            gc.collect()
            if not waiter.wait(7):
                raise Exception("Not properly cleaned up!")


skiplist = ('IopsTest', 'LockmodeTest', 'PipelineTest')

configured_classes = get_configured_classes(GEventImplMixin,
                                            skiplist=skiplist)

# View iterator test no longer works because of missing include_docs
def viter_skipfn(*args):
    raise SkipTest("include_docs not provided on client, "
                   "and no longer supported by server")


for n in ('test_include_docs', 'test_row_processor'):
    setattr(configured_classes['ViewIteratorTest_Bucket'], n, viter_skipfn)

globals().update(configured_classes)
