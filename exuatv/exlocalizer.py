'''
	exlocalizer.py
	exlocalizer provides runtime accessible localized strings
	Copyright (C) 2011 Sergey Maysak a.k.a. sam

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__author__="sam"
__date__ ="$Aug 27, 2011 23:25:46 PM$"

import mc
import exmodel
import xbmc

'''
Concrete subclass of exmodel.localizer interface.
Implements runtime-based localization for boxee UI due to issue with
mc.GetLocalizedString(id) which is not working for custom localized strings
in xml.
In addition, it allows to handle licalized strings in native form - by requesting
actual string to be localized instead of integer id that is hard to manage and
read in code.
Principal method is localizedString.
'''
class exlocalizer(exmodel.localizer):
	localizations = {
		'Russian': {
			'[B]Comments[/B]\n\n': '[B]Комментарии[/B]\n\n',
			'Next': 'Далее',
		},
	}
	language = 'English'

	def __init__(self):
		self.language = xbmc.getLanguage()
		mc.LogInfo("Current language: %s" % self.language)

	def localizedString(self, text):
		try:
			return self.localizations[self.language][text]
		except:
			return text
