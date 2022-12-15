
class Fraction:
    def __init__(self) -> None:
        pass
    def __init__(self, n, d):
        self.num = int(n)
        self.den = int(d)    
    def print (self):
        print("Fraction: ",self.num, "/", self.den)
    def float_value(self):
        i = self.num/self.den 
        return print("Float value: ",i)
    def short(self):
        n = self.num
        d = self.den
        
        for i in range(1,5):  
            if n%i == 0 and d%i == 0:
                n= n/i 
                d =d/i
                i=1
        print("Shorter fraction: ",int(n),"/",int(d))


fr = Fraction(12,15)
fr.print()
fr.float_value()
fr.short()
