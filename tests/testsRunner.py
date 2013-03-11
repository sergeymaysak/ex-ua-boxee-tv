# -*- coding: utf-8 -*-

#  testsRunner.py
#  exuatv
#
#  Created by Sergey Maysak on 1/12/13.
#

import unittest
import testExModel
import testFsModel
#import <another module>

suite = unittest.TestSuite()
#suite.addTest(testExModel.suite())
suite.addTest(testFsModel.suite())
#suite.addTest(<add another suite here>)
unittest.TextTestRunner(verbosity=2).run(suite)

#if __name__ == '__main__':
#	unittest.main()
