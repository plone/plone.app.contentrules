from Acquisition import aq_base
from lxml import etree
from plone.app.contentrules import api
from plone.app.contentrules.exportimport.interfaces import (
    IRuleElementExportImportHandler,
)
from plone.app.contentrules.rule import get_assignments
from plone.app.contentrules.rule import Rule
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.contentrules.rule.interfaces import IRuleElement
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.supermodel.utils import elementToValue
from plone.supermodel.utils import valueToElement
from Products.CMFCore.interfaces import ISiteRoot
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import _getDottedName
from Products.GenericSetup.utils import _resolveDottedName
from Products.GenericSetup.utils import XMLAdapterBase
from xml.dom import minidom
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.container.interfaces import INameChooser
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode


def as_bool(string, default=False):
    if string is None or not str(string):
        return default
    return string.lower() == "true"


@adapter(Interface)
@implementer(IRuleElementExportImportHandler)
class PropertyRuleElementExportImportHandler:
    """Import portlet assignment settings based on zope.schema properties"""

    def __init__(self, element):
        data = IRuleElementData(element)
        self.element = element
        self.descriptor = getUtility(IRuleElement, name=data.element)

    def import_element(self, node):

        if self.descriptor.schema is None:
            return

        for child in node.childNodes:
            if child.nodeName == "property":
                self.import_node(self.descriptor.schema, child)

    def export_element(self, doc, node):
        if self.descriptor.schema is None:
            return

        for field_name in self.descriptor.schema:
            field = self.descriptor.schema[field_name]

            if not IField.providedBy(field):
                continue

            child = self.export_field(doc, field)
            node.appendChild(child)

    # Helper methods

    def import_node(self, interface, child):
        """Import a single <property /> node"""
        property_name = child.getAttribute("name")

        field = interface.get(property_name, None)
        if field is None:
            return

        field = field.bind(self.element)
        # child is minidom but supermodel needs an etree node so we need to convert it
        child = etree.fromstring(child.toxml())

        value = elementToValue(field, child)

        field.validate(value)
        field.set(self.element, value)

    def export_field(self, doc, field):
        """Turn a zope.schema field into a node and return it"""

        field = field.bind(self.element)
        value = field.get(self.element)

        child = doc.createElement("property")
        child.setAttribute("name", field.__name__)

        # supermodel gives us an etree node but GS uses minidom so we need to convert it
        node = valueToElement(field, value)
        if node.text:
            child.appendChild(doc.createTextNode(str(node.text)))
        # Assumes there are not other text nodes and we can throw away the parent node
        for node in node.iterchildren():
            xml = etree.tostring(node, encoding="utf8")
            child.appendChild(minidom.parseString(xml).firstChild)
        return child


@adapter(ISiteRoot, ISetupEnviron)
@implementer(IBody)
class RulesXMLAdapter(XMLAdapterBase):
    """In- and exporter for a local portlet configuration"""

    name = "contentrules"
    _LOGGER_ID = "contentrules"

    def _exportNode(self):
        """Export rules"""
        node = self._doc.createElement("contentrules")
        child = self._extractRules()
        if child is not None:
            node.appendChild(child)
        self._logger.info("Content rules exported")
        return node

    def _importNode(self, node):
        """Import rules"""
        if self.environ.shouldPurge():
            self._purgeRules()
        self._initRules(node)
        self._logger.info("Content rules imported")

    def _purgeRules(self):
        """Purge all registered rules"""
        storage = queryUtility(IRuleStorage)
        if storage is not None:
            # If we delete a rule, assignments will be removed as well
            for k in list(storage.keys()):
                del storage[k]

    def _initRules(self, node):
        """Import rules from the given node"""

        site = self.environ.getSite()
        storage = queryUtility(IRuleStorage)
        if storage is None:
            return

        for child in node.childNodes:
            if child.nodeName == "rule":

                rule = None
                name = child.getAttribute("name")
                if name:
                    rule = storage.get(name, None)

                if rule is None:
                    rule = Rule()

                    if not name:
                        chooser = INameChooser(storage)
                        name = chooser.chooseName(None, rule)

                    storage[name] = rule
                else:
                    # Clear out conditions and actions since we're expecting
                    # new ones
                    del rule.conditions[:]
                    del rule.actions[:]

                rule.title = child.getAttribute("title")
                rule.description = child.getAttribute("description")
                event_name = child.getAttribute("event")
                rule.event = _resolveDottedName(event_name)
                if not rule.event:
                    raise ImportError(f"Can not import {event_name}")

                rule.enabled = as_bool(child.getAttribute("enabled"), True)
                rule.stop = as_bool(child.getAttribute("stop-after"))
                rule.cascading = as_bool(child.getAttribute("cascading"))
                # Aq-wrap to enable complex setters for elements below
                # to work

                rule = rule.__of__(site)

                for rule_config_node in child.childNodes:
                    if rule_config_node.nodeName == "conditions":
                        for condition_node in rule_config_node.childNodes:
                            if not condition_node.nodeName == "condition":
                                continue

                            type_ = condition_node.getAttribute("type")
                            element_type = getUtility(IRuleCondition, name=type_)
                            if element_type.factory is None:
                                continue

                            condition = element_type.factory()

                            # Aq-wrap in case of complex setters
                            condition = condition.__of__(rule)

                            handler = IRuleElementExportImportHandler(condition)
                            handler.import_element(condition_node)

                            rule.conditions.append(aq_base(condition))

                    elif rule_config_node.nodeName == "actions":
                        for action_node in rule_config_node.childNodes:
                            if not action_node.nodeName == "action":
                                continue

                            type_ = action_node.getAttribute("type")
                            element_type = getUtility(IRuleAction, name=type_)
                            if element_type.factory is None:
                                continue

                            action = element_type.factory()

                            # Aq-wrap in case of complex setters
                            action = action.__of__(rule)

                            handler = IRuleElementExportImportHandler(action)
                            handler.import_element(action_node)

                            rule.actions.append(aq_base(action))

            elif child.nodeName == "assignment":
                location = child.getAttribute("location")
                if location.startswith("/"):
                    location = location[1:]

                try:
                    container = site.unrestrictedTraverse(str(location))
                except KeyError:
                    continue

                name = child.getAttribute("name")
                api.assign_rule(
                    container,
                    name,
                    enabled=as_bool(child.getAttribute("enabled")),
                    bubbles=as_bool(child.getAttribute("bubbles")),
                    insert_before=child.getAttribute("insert-before"),
                )

    def _extractRules(self):
        """Extract rules to a document fragment"""

        site = self.environ.getSite()
        storage = queryUtility(IRuleStorage)
        if storage is None:
            return
        fragment = self._doc.createDocumentFragment()

        assignment_paths = set()

        for name, rule in sorted(storage.items()):
            rule_node = self._doc.createElement("rule")

            rule_node.setAttribute("name", name)
            rule_node.setAttribute("title", rule.title)
            rule_node.setAttribute("description", rule.description)
            rule_node.setAttribute("event", _getDottedName(rule.event))
            rule_node.setAttribute("enabled", str(rule.enabled))
            rule_node.setAttribute("stop-after", str(rule.stop))
            rule_node.setAttribute("cascading", str(rule.cascading))
            # Aq-wrap so that exporting fields with clever getters or
            # vocabularies will work. We also aq-wrap conditions and
            # actions below.

            rule = rule.__of__(site)

            # Add conditions
            conditions_node = self._doc.createElement("conditions")
            for condition in rule.conditions:
                condition_data = IRuleElementData(condition)
                condition = condition.__of__(rule)

                condition_node = self._doc.createElement("condition")
                condition_node.setAttribute("type", condition_data.element)

                handler = IRuleElementExportImportHandler(condition)
                handler.export_element(self._doc, condition_node)
                conditions_node.appendChild(condition_node)
            rule_node.appendChild(conditions_node)

            # Add actions
            actions_node = self._doc.createElement("actions")
            for action in rule.actions:
                action_data = IRuleElementData(action)
                action = action.__of__(rule)

                action_node = self._doc.createElement("action")
                action_node.setAttribute("type", action_data.element)

                handler = IRuleElementExportImportHandler(action)
                handler.export_element(self._doc, action_node)
                actions_node.appendChild(action_node)
            rule_node.appendChild(actions_node)

            fragment.appendChild(rule_node)
            assignment_paths.update(get_assignments(rule))
        # Export assignments last - this is necessary to ensure they
        # are orderd properly

        site_path_length = len("/".join(site.getPhysicalPath()))
        for path in sorted(assignment_paths):
            try:
                container = site.unrestrictedTraverse(path)
            except KeyError:
                continue

            assignable = IRuleAssignmentManager(container, None)
            if assignable is None:
                continue

            location = path[site_path_length:]
            for name, assignment in sorted(assignable.items()):
                assignment_node = self._doc.createElement("assignment")
                assignment_node.setAttribute("location", location)
                assignment_node.setAttribute("name", name)
                assignment_node.setAttribute("enabled", str(assignment.enabled))
                assignment_node.setAttribute("bubbles", str(assignment.bubbles))
                fragment.appendChild(assignment_node)

        return fragment


def importRules(context):
    """Import content rules"""
    site = context.getSite()
    importer = queryMultiAdapter((site, context), IBody, name="plone.contentrules")
    if importer is not None:
        filename = f"{importer.name}{importer.suffix}"
        body = context.readDataFile(filename)
        if body is not None:
            importer.filename = filename  # for error reporting
            importer.body = body


def exportRules(context):
    """Export content rules"""
    site = context.getSite()
    exporter = queryMultiAdapter((site, context), IBody, name="plone.contentrules")
    if exporter is not None:
        filename = f"{exporter.name}{exporter.suffix}"
        body = exporter.body
        # make sure it's encoded as earlier version of GS didn't do this
        if isinstance(body, str):
            encoding = context.getEncoding() or "utf-8"
            body = body.encode(encoding)
        if body is not None:
            context.writeDataFile(filename, body, exporter.mime_type)
