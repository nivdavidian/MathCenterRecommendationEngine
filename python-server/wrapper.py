
class Wrapper:
    def __init__(self) -> None:
        self.wrapped: Wrapper = None
    def run(self, func):
        func()
        if self.wrapped is None:
            return
        self.wrapped.run()
    
    
def wrap(objs: list[Wrapper]):
    first = objs[0]
    last = first
    for o in objs[1:]:
        last.wrapped = o
        last = o
        
    return first