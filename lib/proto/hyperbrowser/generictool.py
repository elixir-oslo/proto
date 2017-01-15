# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.
#

from proto.generictool import GenericToolController
from HyperBrowserControllerMixin import HyperBrowserControllerMixin


class HBGenericToolController(HyperBrowserControllerMixin, GenericToolController):
    def _init(self):
        super(HBGenericToolController, self)._init()

    def _executeTool(self, toolClassName, choices, galaxyFn, username):
        super(HBGenericToolController, self)._executeTool(
            toolClassName, choices, galaxyFn, username)


def getController(transaction = None, job = None):
    return HBGenericToolController(transaction, job)
