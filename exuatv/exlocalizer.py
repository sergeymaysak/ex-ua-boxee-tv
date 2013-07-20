# -*- coding: utf-8 -*-
'''
	exlocalizer.py
	exlocalizer provides runtime accessible localized strings
	Copyright (C) 2011-2013 Sergey Maysak a.k.a. sam (segey.maysak@gmail.com)

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

exSharedLocalizer = None #holds the global localizer object

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
class exlocalizer:
	LOCALIZATIONS = {
		'Russian': {
			'[B]Comments[/B]\n\n': '[B]Комментарии[/B]\n\n',
			'Next': 'Далее',
			'No access to www.ex.ua and fex.net': 'Нет доступа к www.ex.ua и fex.net',
			'Please make sure you have proxy disabled and check access to www.ex.ua or fex.net in internet browser': 'Пожайлуста убедитесь что прокси выключен и проверте доступ к www.ex.ua или fex.net в интернет броузере',
			'Recently Viewed':'Недавно просмотренное',
			'Playback' : 'Воспроизведение',
			'Info' : 'Сведения',
			'Add to Favorites' : 'Добавить в Избранное',
			'Remove from Favorites' : 'Удалить из Избранного'
		},
	}

	def __init__(self):
		try:
			import mc
			import xbmc
			self.language = xbmc.getLanguage()
			mc.LogInfo("Current language: %s" % self.language)
		except:
			pass

	def localizedString(self, text):
		try:
			return self.LOCALIZATIONS[self.language][text]
		except:
			return text


def GetSharedLocalizer():
	global exSharedLocalizer
	if (exSharedLocalizer is None):
		exSharedLocalizer = exlocalizer()
	return exSharedLocalizer