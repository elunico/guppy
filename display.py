class DisplayObject:
    def __init__(self, data):
        self.data = data

    def display(self):
        raise NotImplementedError(
            'Implement Display on subclass of DisplayObject')
