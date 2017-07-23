from collections import namedtuple

DisplayData = namedtuple('DisplayData', 'display replacement')
Crumblist = namedtuple('Crumblist', 'subtype crumbs')
Element = namedtuple('Element', 'subtype text meta')
Choice = namedtuple('Choice', 'situation options')
Option = namedtuple('Option', 'to level text')

class Meta:
    def __init__(self, element, elem_id, overlay_pos=None, subset=-1):
        self.element = element
        self.cache_id = elem_id
        self.display = True if overlay_pos else False
        self.position = overlay_pos
        self.subset = subset

    def __str__(self):
        return self.element.text

    def copy(self):
        # don't copy the display information
        return Meta(self.element, self.cache_id, [], self.subset)

class Instructions:
    def __init__(self, class_type, sub_type, type_indicator, contents):
        self.class_type = class_type
        self.sub_type = sub_type
        self.contents = contents
        self.type_indicator = type_indicator

class Canvas:
    def __init__(self, type_id, background, overlay, static=None):
        self.type_id = type_id
        self.background = background
        self.overlay = overlay
        self.static = static