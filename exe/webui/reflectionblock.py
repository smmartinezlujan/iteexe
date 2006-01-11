# ===========================================================================
# eXe 
# Copyright 2004-2005, University of Auckland
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================
"""
ReflectionBlock can render and process ReflectionIdevices as XHTML
"""

import logging
from exe.webui.block               import Block
from exe.webui                     import common

log = logging.getLogger(__name__)


# ===========================================================================
class ReflectionBlock(Block):
    """
    ReflectionBlock can render and process ReflectionIdevices as XHTML
    """
    def __init__(self, parent, idevice):
        """
        Initialize a new Block object
        """
        Block.__init__(self, parent, idevice)
        self.activity        = idevice.activity 
        self.answer          = idevice.answer
        self.activityInstruc = idevice.activityInstruc
        self.answerInstruc   = idevice.answerInstruc


    def process(self, request):
        """
        Process the request arguments from the web server
        """
        Block.process(self, request)
        
        if "activity"+self.id in request.args:
            self.idevice.activity = request.args["activity"+self.id][0]

        if "answer"+self.id in request.args:
            self.idevice.answer = request.args["answer"+self.id][0]
        
        if "title"+self.id in request.args:
            self.idevice.title = request.args["title"+self.id][0]
        

    def renderEdit(self, style):
        """
        Returns an XHTML string with the form element for editing this block
        """
        html  = "<div class=\"iDevice\"><br/>\n"
        html += common.textInput("title"+self.id, self.idevice.title)
        html += u"<br/><br/>\n"
        html += "<b>" + _(u"Reflective question:") + "</b>"
        html += common.elementInstruc("activity"+self.id, self.activityInstruc)
        html += "<br/>" + common.richTextArea("activity"+self.id, self.activity)
        html += "<b>" + _("Feedback:") + "</b>"
        html += common.elementInstruc("answer"+self.id, self.answerInstruc)
        html += "<br/>" + common.richTextArea("answer"+self.id, self.answer)
        html += "<br/>" + self.renderEditButtons()
        html += "</div>\n"
        return html


    def renderViewContent(self):
        """
        Returns an XHTML string for this block
        """
        html  = u'<script type="text/javascript" src="common.js"></script>\n'
        html += u'<div class="iDevice_inner">\n'
    
        html += self.activity   
        html += '<div id="view%s" style="display:block;">' % self.id
        html += '<input type="button" name="btnshow%s" ' % self.id
        html += 'value ="%s" ' % _(u"Click here")
        html += 'onclick="showAnswer(\'%s\',1)"/></div>\n ' % self.id
        html += '<div id="hide%s" style="display:none;">' % self.id
        html += '<input type="button" name="btnhide%s" '  % self.id 
        html += 'value="%s" ' % _(u"Hide")
        html += 'onclick="showAnswer(\'%s\',0)"/></div>\n ' % self.id
        html += '<div id="s%s" class="feedback" style=" ' % self.id
        html += 'display: none;">'
        html += self.answer
        html += "</div>\n"
        html += "</div>\n"
        return html
    

from exe.engine.reflectionidevice  import ReflectionIdevice
from exe.webui.blockfactory        import g_blockFactory
g_blockFactory.registerBlockType(ReflectionBlock, ReflectionIdevice)    

# ===========================================================================
