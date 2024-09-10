# encoding: utf-8

###########################################################################################################
#
#
# Palette Plugin
#
# Read the docs:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Palette
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import Glyphs, GSEditViewController, UPDATEINTERFACE
from GlyphsApp.plugins import PalettePlugin


class AnchorComponents (PalettePlugin):
	dialog = objc.IBOutlet()
	compNameField = objc.IBOutlet()
	anchorNameField = objc.IBOutlet()
	propagateButton = objc.IBOutlet()


	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'Anchor Components',
			'de': 'Komponenten verankern',
			'es': 'Anclar componentes',
			'pt': 'Âncoras dos componentes',
		})

		# Load .nib dialog (without .extension)
		self.loadNib('IBdialog', __file__)


	@objc.python_method
	def start(self):
		# Adding a callback for the 'GSUpdateInterface' event
		Glyphs.addCallback(self.update, UPDATEINTERFACE)


	@objc.python_method
	def __del__(self):
		Glyphs.removeCallback(self.update)


	@objc.IBAction
	def propagate_(self, sender):
		thisLayer = Glyphs.font.currentTab.activeLayer()
		if thisLayer is None:
			self.propagateButton.setEnabled_(False)
			return

		self.propagateButton.setEnabled_(True)
		componentStructure = thisLayer.componentNames()
		glyph = thisLayer.parent
		for layer in glyph.layers:
			if layer is thisLayer:
				continue
			layer.setComponentNames_(componentStructure)
			if layer.compareString() != thisLayer.compareString():
				continue
			for i, accentComponent in enumerate(layer.components):
				if i < 1:
					continue
				accentComponent.setAnchor_(thisLayer.components[i].anchor)


	@objc.IBAction
	def anchorComponent_(self, sender):
		thisLayer = Glyphs.font.currentTab.activeLayer()
		if thisLayer is None:
			self.propagateButton.setEnabled_(False)
			return
		
		self.propagateButton.setEnabled_(True)
		if thisLayer.selection is None:
			return
		
		newAnchor = None
		if self.anchorNameField.stringValue():
			newAnchor = self.anchorNameField.stringValue()
		
		for selectedComponent in thisLayer.components:
			if selectedComponent.selected and selectedComponent.name == self.compNameField.stringValue():
				selectedComponent.anchor = newAnchor


	@objc.python_method
	def update(self, sender):
		currentTab = sender.object()
		selectedComponent = None
		if isinstance(currentTab, GSEditViewController):
			# We’re in the Edit View
			# Check whether glyph is being edited
			layer = currentTab.activeLayer()
			if layer is None:
				self.propagateButton.setEnabled_(False)
			else:
				self.propagateButton.setEnabled_(True)
				for selectedComponent in layer.components:
					if selectedComponent in layer.selection:
						self.compNameField.setStringValue_(selectedComponent.name)
						self.anchorNameField.removeAllItems()
						
						if selectedComponent.anchor:
							self.anchorNameField.setStringValue_(selectedComponent.anchor)
						else:
							self.anchorNameField.setStringValue_("")
							
						listOfAnchors = []
						for otherComponent in layer.components:
							relevantAnchors = [a.name for a in otherComponent.componentLayer.anchors if not a.name.startswith("_") and not a.name.startswith("#_") and not "entry" in a.name]
							listOfAnchors.extend(relevantAnchors)
						listOfAnchors = sorted(set(listOfAnchors))
						self.anchorNameField.addItemsWithObjectValues_(listOfAnchors)
							
						return

		self.compNameField.setStringValue_("(select a component)")


	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
