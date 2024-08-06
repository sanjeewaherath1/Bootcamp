list = [2, 3, 5, 7, 11, 13, 17, 19, 23]

import array
numbers = array.array('i', range(5))
print(numbers)
numbers.append(4)
print(list)

print(numbers)

for number in numbers:
    print(number)
