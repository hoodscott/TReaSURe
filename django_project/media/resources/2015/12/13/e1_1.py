#function to calculate the sum of numbers divisible by x and y, up to max
def e1(x, y, max):
    # calculate euler total
    def euler(base, max):
        occurences = int((max-1)/base)
        return (base * occurences * (occurences+1))/2
    #add and remove duplicates
    return euler(x,max) + euler(y,max) - euler(x*y,max)

print e1(3,5,1000)
