#!/usr/bin/python
# -*- coding: utf-8 -*-
# ===========================================================================
# eXeLearning
# Copyright 2017, CeDeC
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.
# ===========================================================================
"""
The TemplateManagerPage is responsible for managing templates
"""

import json
import logging
import os
from zipfile                   import ZipFile

from exe.engine.path import Path
from exe.engine.template      import Template
from exe.webui.livepage        import allSessionClients
from exe.webui.renderable      import RenderableResource


log = logging.getLogger(__name__)


class ImportTemplateError(Exception):
    pass


class ImportTemplateExistsError(ImportTemplateError):
    def __init__(self, local_template, absolute_template_dir, message=''):
        self.local_template = local_template
        self.absolute_template_dir = absolute_template_dir
        if message == '':
            self.message = u'Error importing template, local template already exists. '
        else:
            self.message = message

    def __str__(self):
        return self.message

    pass


class TemplateManagerPage(RenderableResource):
    """
    The TemplateManagerPage is responsible for managing templates
    import / export / delete
    """

    name = 'templatemanager'

    def __init__(self, parent):
        """
        Initialize
        """
        RenderableResource.__init__(self, parent)
        self.action = ""
        self.properties = ""
        self.template = ""
        self.client = None

    def render_GET(self, request):
        """Called for all requests to this object

        Every JSON response sent must have an 'action' field, which value will
        determine the panel to be displayed in the WebUI
        """

        if self.action == 'Properties':
            response = json.dumps({
                                   'success': True,
                                   'properties': self.properties,
                                   'template': self.template,
                                   'action': 'Properties'})
        elif self.action == 'PreExport':
            response = json.dumps({
                                   'success': True,
                                   'properties': self.properties,
                                   'template': self.template,
                                   'action': 'PreExport'})          
        else:
            response = json.dumps({
                                   'success': True,
                                   'templates': self.renderListTemplates(),
                                   'action': 'List'})
            
        self.action = 'List'
        return response

    def render_POST(self, request):
        """ Called on client form submit

        Every form received must have an 'action' field, which value determines
        the function to be executed in the server side.
        The self.action attribute will be sent back to the client (see render_GET)
        """
        self.reloadPanel(request.args['action'][0])

        if request.args['action'][0] == 'doExport':
            self.doExportTemplate(request.args['template'][0],
                               request.args['filename'][0])
        elif request.args['action'][0] == 'doDelete':
            self.doDeleteTemplate(request.args['template'][0])
        elif request.args['action'][0] == 'doImport':
            try:
                self.doImportTemplate(request.args['filename'][0])
                self.alert(
                           _(u'Success'),
                           _(u'Successfully imported template'))
            except Exception, e:
                self.alert(
                           _(u'Error'),
                           _(u'Error while installing template: %s') % str(e))
        elif request.args['action'][0] == 'doProperties':
            self.doPropertiesTemplate(request.args['template'][0])
        elif request.args['action'][0] == 'doPreExport':
            self.doPreExportTemplate(request.args['template'][0])
        elif request.args['action'][0] == 'doList':
            self.doList()

        return ''

    def reloadPanel(self, action):
        
        self.client.sendScript('Ext.getCmp("templatemanagerwin").down("form").reload("%s")' % (action),
                               filter_func=allSessionClients)

    def alert(self, title, mesg):
        
        self.client.sendScript('Ext.Msg.alert("%s","%s")' % (title, mesg),
                               filter_func=allSessionClients)

    def renderListTemplates(self):
        """
        Returns a JSON response with a list of the installed templates
        and its related buttons
        """
        templates = []
        templateStores = self.templateStore.getTemplates()

        for template in templateStores:
                export = True
                delete = False
                properties = True
                if template.name != 'Base' and template.name != self.config.defaultContentTemplate :
                    delete = True
                templates.append({'template': template.file,
                               'name': template.filename,
                               'exportButton': export,
                               'deleteButton': delete,
                               'propertiesButton': properties})
        return templates

    def doImportTemplate(self, filename):
        """ Imports an template from a ELT file

        Checks that it is a valid template file,
        that the directory does not exist (prevent overwriting)
        """
        
        templateDir = self.config.webDir / 'content_template'
        log.debug("Import template from %s" % filename)
        
        filename = Path(filename)
        baseFile = filename.basename()
        absoluteTargetDir = templateDir / baseFile
        
        try:
            ZipFile(filename, 'r')
        except IOError:
            raise ImportTemplateError('Can not create dom object')

        if os.path.exists(absoluteTargetDir):
            
            template = Template(absoluteTargetDir)
            raise ImportTemplateExistsError(template, absoluteTargetDir, u'template already exists')
        else:
            
            filename.copyfile(absoluteTargetDir)
            template = Template(absoluteTargetDir)
            
            if template.isValid():
                
                    if not self.templateStore.addTemplate(template):
                        
                        absoluteTargetDir.remove()
                        raise ImportTemplateExistsError(template, absoluteTargetDir, u'The template name already exists')
            else:
                
                absoluteTargetDir.remove()
                raise ImportTemplateExistsError(template, absoluteTargetDir, u'Incorrect template format')

        self.action = ""

    def doExportTemplate(self, template, filename):

        if filename != '':
            templateDir = self.config.webDir / 'content_template'
            templateExport = Template(templateDir / template)
            self.__exportTemplate(templateExport, unicode(filename))

    def __exportTemplate(self, dirTemplateName, filename):
        """ Exports template """
        if not filename.lower().endswith('.elt'):
            filename += '.elt'
        sfile = os.path.basename(filename)
        log.debug("Export template %s" % dirTemplateName)
        try:
            dirTemplateName.path.copyfile(filename)
            
            self.alert(_(u'Correct'),
                       _(u'template exported correctly: %s') % sfile)
        except IOError:
            self.alert(_(u'Error'),
                       _(u'Could not export template : %s') % filename.basename())
        self.action = ""

    def doDeleteTemplate(self, template):

        try:
            templateDir = self.config.webDir / 'content_template'
            templateDelete = Template(templateDir / template)
            self.__deleteTemplate(templateDelete)
            self.alert(_(u'Correct'), _(u'template deleted correctly'))
            self.reloadPanel('doList')
        except:
            self.alert(_(u'Error'), _(u'An unexpected error has occurred'))
        self.action = ""

    def __deleteTemplate(self, template):
        """ Deletes the given template from local installation """
        log.debug("delete template")
        templatePath = template.path
        templatePath.remove()
        self.templateStore.delTemplate(template)

    def doPropertiesTemplate(self, template):
        
        templateDir = self.config.webDir / 'content_template'
        templateProperties = Template(templateDir / template)
        self.properties = templateProperties._renderProperties()
        self.action = 'Properties'
        self.template = templateProperties.name
        
    def doPreExportTemplate(self, template):
        
        templateDir = self.config.webDir / 'content_template'
        templateExport = Template(templateDir / template)
        self.properties = templateExport._renderProperties()
        self.action = 'PreExport'
        self.template = template

    def doList(self):
        
        self.action = 'List'
        self.template = ''
        