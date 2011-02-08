class Images(object):
    def __init__(self, CNX):
        self._images = CNX.images.list()
        self.global_images = [ img for img in self._images if not 'created' in img._info ]
        self.local_images = [ img for img in self._images if 'created' in img._info ]
        self.global_images.sort(key=lambda x: x.name.lower())
        self.local_images.sort(key=lambda x: x.name.lower())
        self.all_images=self.global_images
        self.all_images.extend(self.local_images)
        self.current = 0
        self.high = len(self.all_images)
        
    def __iter__(self):
        return self

    def __getitem__(self, key):
        if type(key) is int:
            return self.all_images[key]
        for x in self.all_images:
            if x.name == key:
                return x
        raise KeyError(key)

    def __contains__(self, key):
        try:
            return self[key]
        except(KeyError):
            pass
    
    def __len__(self):
        return  self.high

    def next(self):
        if self.current >= self.high:
            raise StopIteration
        else:
            ret = self.all_images[self.current]
            self.current += 1
            return ret

    def __call__(self):
        return self.all_images
        
if __name__ == '__main__':
    from lib.common import CNX
    images = Images(CNX)
    print images()
