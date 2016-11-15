from PIL import Image, ImageFilter

class CustomFilters:
    def __init__(self, filters_names, img):
        self.filters_names = filters_names
        self.img = img

    def apply_all(self):
        for name in self.filters_names:
            self.img = getattr(self, name)(self.img)
        return self.img

    def grayscale(self, img):
        return img.convert('LA')