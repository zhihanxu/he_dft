N = 2**16
rotate_amount = 2048
rotate_times = 31

result_list = []

def power_of_5(exponent):
    result = 1
    for j in range(rotate_times):
        exponent = (j+1) * rotate_amount
        for i in range(exponent):
            result = result * 5
            result = result % N
        result_list.append(result)


# print result list
power_of_5(rotate_amount)
print("power_of_5 list:", result_list, "\nlength:", len(result_list))