import math

class ease():
    def process_ease(self, x, dir):
        if x < 0: x = 0
        match dir:
            case "out": return self.tween_out(x)
            case "in": return self.tween_in(x)
            case "in-out": return self.tween_in_out(x)
            case _: return self.tween_out(x)

    def tween_out(x):
        pass

    def tween_in(x):
        pass

    def tween_in_out(x):
        pass

class cubic(ease):
    def tween_out(self, x):
        return 1 - pow(1 - x, 3)

    def tween_in(self, x):
        return x * x * x

    def tween_in_out(self, x):
        if x < 0.5: return 4 * x * x * x
        else: return 1 - pow(-2 * x + 2, 3) / 2

class sine(ease):
    def tween_out(self, x):
        return math.sin((x * math.pi) / 2)

    def tween_in(self, x):
        return 1 - math.cos((x * math.pi) / 2)

    def tween_in_out(self, x):
        return -(math.cos(math.PI * x) - 1) / 2

class quad(ease):
    def tween_out(self, x):
        return 1 - (1 - x) * (1 - x)

    def tween_in(self, x):
        return x * x

    def tween_in_out(self, x):
        if x < 0.5: return 2 * x * x
        else: return 1 - pow(-2 * x + 2, 2) / 2

class quint(ease):
    def tween_out(self, x):
        return 1 - pow(1 - x, 5)

    def tween_in(self, x):
        return x * x * x * x * x

    def tween_in_out(self, x):
        if x < 0.5: return 16 * x * x * x * x * x
        else: return 1 - pow(-2 * x + 2, 5) / 2

class quart(ease):
    def tween_out(self, x):
        return 1 - pow(1 - x, 4)

    def tween_in(self, x):
        return x * x * x * x

    def tween_in_out(self, x):
        if x < 0.5: return 8 * x * x * x * x
        else: return 1 - pow(-2 * x + 2, 4) / 2

class expo(ease):
    def tween_out(self, x):
        if x == 1: return 1
        else: return 1 - pow(2, -10 * x)

    def tween_in(self, x):
        if x == 0: return 0
        else: return pow(2, 10 * x - 10)

    def tween_in_out(self, x):
        if x == 0: return 0
        elif x == 1: return 1
        elif x < 0.5: return pow(2, 20 * x - 10) / 2
        else: return (2 - pow(2, -20 * x + 10)) / 2

class circ(ease):
    def tween_out(self, x):
        return math.sqrt(1 - pow(x - 1, 2))

    def tween_in(self, x):
        return 1 - math.sqrt(1 - pow(x, 2))

    def tween_in_out(self, x):
        if x < 0.5: return (1 - math.sqrt(1 - math.pow(2 * x, 2))) / 2
        else: return (math.sqrt(1 - math.pow(-2 * x + 2, 2)) + 1) / 2

class back(ease):
    def tween_out(self, x):
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)

    def tween_in(self, x):
        c1 = 1.70158
        c3 = c1 + 1
        return c3 * x * x * x - c1 * x * x

    def tween_in_out(self, x):
        c1 = 1.70158
        c2 = c1 * 1.525

        if x < 0.5: return (pow(2 * x, 2) * ((c2 + 1) * 2 * x - c2)) / 2
        else: return (pow(2 * x - 2, 2) * ((c2 + 1) * (x * 2 - 2) + c2) + 2) / 2
    
class elastic(ease):
    def tween_out(self, x):
        c4 = (2 * math.pi) / 3
        if x == 0: return 0
        elif x == 1: return 1
        else: return math.pow(2, -10 * x) * math.sin((x * 10 - 0.75) * c4) + 1

    def tween_in(self, x):
        c4 = (2 * math.pi) / 3
        if x == 0: return 0
        elif x == 1: return 1
        else: return -math.pow(2, 10 * x - 10) * math.sin((x * 10 - 10.75) * c4)

    def tween_in_out(self, x):
        c5 = (2 * math.pi) / 4.5
        if x == 0: return 0
        elif x == 1: return 1
        elif x < 0.5: return -(pow(2, 20 * x - 10) * math.sin((20 * x - 11.125) * c5)) / 2
        else: return (pow(2, -20 * x + 10) * math.sin((20 * x - 11.125) * c5)) / 2 + 1
    
class bounce(ease):
    def tween_out(self, x):
        n1 = 7.5625
        d1 = 2.75

        if (x < 1 / d1): return n1 * x * x
        elif (x < 2 / d1):
            x -= 1.5 / d1
            return n1 * x * x + 0.75
        elif (x < 2.5 / d1):
            x -= 2.25 / d1
            return n1 * x * x + 0.9375
        else:
            x -= 2.65 / d1
            return n1 * x * x + 0.984375

    def tween_in(self, x):
        return 1 - self.tween_out(1-x)

    def tween_in_out(self, x):
        if x < 0.5: return (1 - self.tween_out(1 - 2 * x)) / 2
        else: return (1 + self.tween_out(2 * x - 1)) / 2


class linear(ease):
    def process_ease(self, x, d):
        return x

eases = {
    "cubic": cubic(),
    "quad": quad(),
    "quart": quart(),
    "quint": quint(),
    "circ": circ(),
    "back": back(),
    "elastic": elastic(),
    "bounce": bounce(),
    "expo": expo(),
    "linear": linear()
}