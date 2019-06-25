##
# UefiBuild Plugin that supports Window Capsule files based on the
# Windows Firmware Update Platform spec.
# Creates INF, Cat, and then signs it
#
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause-Patent

# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

import sys
import re
import datetime
import os
import logging
from MuEnvironment import PluginManager
from MuPythonLibrary.Uefi.Capsule.CatGenerator import *
from MuPythonLibrary.Uefi.Capsule.InfGenerator import *
from MuPythonLibrary.UtilityFunctions import CatalogSignWithSignTool
from MuPythonLibrary.Windows.VsWhereUtilities import FindToolInWinSdk


class WindowsCapsuleSupportHelper(PluginManager.IUefiHelperPlugin):

  def RegisterHelpers(self, obj):
      fp = os.path.abspath(__file__)
      obj.Register("PackageWindowsCapsuleFiles", WindowsCapsuleSupportHelper.PackageWindowsCapsuleFiles, fp)


  @staticmethod
  def PackageWindowsCapsuleFiles(OutputFolder, ProductName, ProductFmpGuid, CapsuleVersion_DotString,
    CapsuleVersion_HexString, ProductFwProvider, ProductFwMfgName, ProductFwDesc, CapsuleFileName, PfxFile=None, PfxPass=None,
    Rollback=False, Arch='amd64', OperatingSystem_String='Win10'):

      logging.debug("CapsulePackage: Create Windows Capsule Files")

      #Make INF
      InfFilePath = os.path.join(OutputFolder, ProductName + ".inf")
      InfTool = InfGenerator(ProductName, ProductFwProvider, ProductFmpGuid, Arch, ProductFwDesc, CapsuleVersion_DotString, CapsuleVersion_HexString)
      InfTool.Manufacturer = ProductFwMfgName  #optional
      ret = InfTool.MakeInf(InfFilePath, CapsuleFileName, Rollback)
      if(ret != 0):
          raise Exception("CreateWindowsInf Failed with errorcode %d" % ret)

      #Make CAT
      CatFilePath = os.path.realpath(os.path.join(OutputFolder, ProductName + ".cat"))
      CatTool = CatGenerator(Arch, OperatingSystem_String)
      ret = CatTool.MakeCat(CatFilePath)

      if(ret != 0):
          raise Exception("Creating Cat file Failed with errorcode %d" % ret)

      if(PfxFile is not None):
          #Find Signtool
          SignToolPath = FindToolInWinSdk("signtool.exe")
          if not os.path.exists(SignToolPath):
              raise Exception("Can't find signtool on this machine.")
          #dev sign the cat file
          ret = CatalogSignWithSignTool(SignToolPath, CatFilePath, PfxFile, PfxPass)
          if(ret != 0):
              raise Exception("Signing Cat file Failed with errorcode %d" % ret)

      return ret
