import math

class Vector2:
    def __init__(self, x : float, y : float):
        self.x = x
        self.y = y
    
    def __add__(self, obj : "Vector2"):
        return Vector2(self.x + obj.x, self.y + obj.y)

    def __sub__(self, obj : "Vector2"):
        return Vector2(self.x - obj.x, self.y - obj.y)
    
    def __mul__(self, obj : float):
        return Vector2(self.x * obj, self.y * obj)

    def __rmul__(self, obj : float):
        return Vector2(self.x * obj, self.y * obj)

    def __truediv__(self, obj : float):
        return Vector2(self.x / obj, self.y / obj)
    
    def __iadd__(self, obj : "Vector2"):
        return Vector2(self.x + obj.x, self.y + obj.y)

    def __isub__(self, obj : "Vector2"):
        return Vector2(self.x - obj.x, self.y - obj.y)
    
    def __imul__(self, obj : float):
        return Vector2(self.x * obj, self.y * obj)

    def __rimul__(self, obj : float):
        return Vector2(self.x * obj, self.y * obj)

    def __idiv__(self, obj : float):
        return Vector2(self.x / obj, self.y / obj)
    
    def __eq__(self, obj: "Vector2") -> bool:
        return self.x == obj.x and self.y == obj.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        length = self.length()
        if (length == 0):
            return Vector2(0, 0)
        return self / length

    def corrected(self) -> "Vector2":
        min_delta = 0.0001
        corrected_vector = Vector2(0, 0)
        #x component
        rounded_x = round(self.x)
        if abs(rounded_x - self.x) < min_delta:
            corrected_vector.x = rounded_x
        else:
            corrected_vector.x = self.x
        
        #y component
        rounded_y = round(self.y)
        if abs(rounded_y - self.y) < min_delta:
            corrected_vector.y = rounded_y
        else:
            corrected_vector.y = self.y
    
        return corrected_vector

    def VectorTo(origin : "Vector2", target : "Vector2", maginude = 1.0):
        return (target - origin).normalized() * maginude

    def truncate(self):
        return Vector2(self.x // 1, self.y // 1)

    def to_tuple(self):
        return (self.x, self.y)

    def from_tuple(tuple : tuple):
        return Vector2(tuple[0], tuple[1])

class Vector2i:
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y
    
    def __add__(self, obj : "Vector2i"):
        return Vector2i(self.x + obj.x, self.y + obj.y)

    def __sub__(self, obj : "Vector2i"):
        return Vector2i(self.x - obj.x, self.y - obj.y)

    def __add__(self, obj : "Vector2"):
        return Vector2(self.x + obj.x, self.y + obj.y)

    def __sub__(self, obj : "Vector2"):
        return Vector2(self.x - obj.x, self.y - obj.y)
    
    def __mul__(self, obj : float):
        return Vector2i(self.x * obj, self.y * obj)

    def __rmul__(self, obj : float):
        return Vector2i(self.x * obj, self.y * obj)

    def __truediv__(self, obj : float):
        return Vector2i(self.x / obj, self.y / obj)
    
    def __iadd__(self, obj : "Vector2i"):
        return Vector2i(self.x + obj.x, self.y + obj.y)

    def __isub__(self, obj : "Vector2i"):
        return Vector2i(self.x - obj.x, self.y - obj.y)
    
    def __iadd__(self, obj : "Vector2"):
        return Vector2(self.x + obj.x, self.y + obj.y)

    def __isub__(self, obj : "Vector2"):
        return Vector2(self.x - obj.x, self.y - obj.y)
    
    def __imul__(self, obj : float):
        return Vector2i(self.x * obj, self.y * obj)

    def __rimul__(self, obj : float):
        return Vector2i(self.x * obj, self.y * obj)

    def __idiv__(self, obj : float):
        return Vector2i(self.x / obj, self.y / obj)
    
    def __eq__(self, obj: "Vector2i") -> bool:
        return self.x == obj.x and self.y == obj.y
    
    def __eq__(self, obj: "Vector2") -> bool:
        return self.x == int(obj.x) and self.y == int(obj.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        length = self.length()
        if (length == 0):
            return Vector2i(0, 0)
        return self / length

    def to_tuple(self):
        return (self.x, self.y)

    def from_tuple(tuple : tuple):
        return Vector2(tuple[0], tuple[1])