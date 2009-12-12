import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tempfile                      import mkdtemp
from shutil                        import rmtree
from Exscript.external.SpiffSignal import Trackable
from Exscript.Log                  import Log
from Exscript.QueueLogger          import QueueLogger

class FakeAction(Trackable):
    failures = 0

    def get_name(self):
        return 'fake'

    def n_failures(self):
        return self.failures

class FakeConnection(Trackable):
    pass

class FakeError(Exception):
    def __init__(self):
        Exception.__init__(self, 'fake error')

class QueueLoggerTest(unittest.TestCase):
    CORRELATE = QueueLogger

    def setUp(self):
        self.logger = QueueLogger()

    def testConstructor(self):
        logger = QueueLogger()

    def testGetLogs(self):
        self.assertEqual(self.logger.get_logs(), {})

        action = FakeAction()
        conn   = FakeConnection()
        self.logger._action_enqueued(action)
        self.assertEqual(self.logger.get_logs(), {})
        self.assertEqual(self.logger.get_logs(action), [])

        action.signal_emit('started', action, conn)
        self.assertEqual(len(self.logger.get_logs()), 1)
        self.assert_(isinstance(self.logger.get_logs(action)[0], Log))
        self.assert_(isinstance(self.logger.get_logs()[action][0], Log))

        conn.signal_emit('data_received', 'hello world')
        self.assertEqual(len(self.logger.get_logs()), 1)
        self.assert_(isinstance(self.logger.get_logs(action)[0], Log))
        self.assert_(isinstance(self.logger.get_logs()[action][0], Log))

        action.signal_emit('succeeded', action)
        self.assertEqual(len(self.logger.get_logs()), 1)
        self.assert_(isinstance(self.logger.get_logs(action)[0], Log))
        self.assert_(isinstance(self.logger.get_logs()[action][0], Log))

    def testGetAbortedLogs(self):
        self.assertEqual(self.logger.get_aborted_logs(), [])

        action = FakeAction()
        conn   = FakeConnection()
        self.logger._action_enqueued(action)
        self.assertEqual(self.logger.get_aborted_logs(), [])

        action.signal_emit('started', action, conn)
        self.assertEqual(self.logger.get_aborted_logs(), [])

        conn.signal_emit('data_received', 'hello world')
        self.assertEqual(self.logger.get_aborted_logs(), [])

        try:
            raise FakeError()
        except Exception, e:
            pass
        action.signal_emit('aborted', action, e)
        self.assertEqual(len(self.logger.get_aborted_logs()), 1)
        self.assert_(isinstance(self.logger.get_aborted_logs()[0], Log))

    def testGetSucceededLogs(self):
        self.assertEqual(self.logger.get_succeeded_logs(), [])

        action = FakeAction()
        conn   = FakeConnection()
        self.logger._action_enqueued(action)
        self.assertEqual(self.logger.get_succeeded_logs(), [])

        action.signal_emit('started', action, conn)
        self.assertEqual(self.logger.get_succeeded_logs(), [])

        conn.signal_emit('data_received', 'hello world')
        self.assertEqual(self.logger.get_succeeded_logs(), [])

        action.signal_emit('succeeded', action)
        self.assertEqual(len(self.logger.get_succeeded_logs()), 1)
        self.assert_(isinstance(self.logger.get_succeeded_logs()[0], Log))

    def testActionEnqueued(self):
        action = FakeAction()
        conn   = FakeConnection()
        self.logger._action_enqueued(action)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(QueueLoggerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())