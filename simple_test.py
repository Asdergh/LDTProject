import numpy as np
import json as js 
import random as rd

def sort_strings_list(strings_list):

    result_strings_list = []
    for string in strings_list:
        
        if (type(string) != float):

            tmp_string_list = string.split()
            curent_list_part = 1
            while curent_list_part < len(tmp_string_list):

                for sub_string_number in range(len(tmp_string_list) - curent_list_part):
                    
                    if (tmp_string_list[sub_string_number][0] > tmp_string_list[sub_string_number + 1][0]):
                        
                        print(tmp_string_list)
                        print(tmp_string_list[sub_string_number])
                        tmp_value = tmp_string_list[sub_string_number]
                        tmp_string_list[sub_string_number] = tmp_string_list[sub_string_number]
                        tmp_string_list[sub_string_number + 1] = tmp_value

                curent_list_part += 1
            result_string = " ".join(sub_string for sub_string in tmp_string_list)
            result_strings_list.append(result_string)
        
        else:
            result_strings_list.append(string)

    return result_strings_list
        
def sort_string(string_to_sort):

    tmp_string_list = string_to_sort.split()
    curent_list_part = 1
    while curent_list_part < len(tmp_string_list):

        for sub_string_number in range(len(tmp_string_list) - curent_list_part):
                    
            if (tmp_string_list[sub_string_number][0] > tmp_string_list[sub_string_number + 1][0]):
                        
                print(tmp_string_list)
                print(tmp_string_list[sub_string_number], tmp_string_list[sub_string_number + 1])
                tmp_string_list[sub_string_number], tmp_string_list[sub_string_number + 1] = \
                    tmp_string_list[sub_string_number + 1], tmp_string_list[sub_string_number]

            curent_list_part += 1
        
    result_string = " ".join(sub_string for sub_string in tmp_string_list)
    return result_string

def sort_numbers(numbers_list):

    curent_list_part = 1
    while curent_list_part < len(numbers_list):

        for sub_string_number in range(len(numbers_list) - curent_list_part):
                    
            if (numbers_list[sub_string_number] > numbers_list[sub_string_number + 1]):
                        
                print(numbers_list)
                print(numbers_list[sub_string_number], numbers_list[sub_string_number + 1])
                numbers_list[sub_string_number], numbers_list[sub_string_number + 1] = \
                    numbers_list[sub_string_number + 1], numbers_list[sub_string_number]

            curent_list_part += 1
        
    return numbers_list


# simbols = ["a", "f", "g", "v", "c", "y"]
# test_strings = []
# for string_number in range(10000):
    
#     rd.shuffle(simbols)
#     tmp_string = " ".join(simbol for simbol in simbols)
#     test_strings.append(tmp_string)

test_string = "я такой молодец и еще я думаю что нельзя так вот прсото меня раздрожать понимашье или нет "
test_array = [9, 2, 3, 5, 6, 7, 8]
result_sorted_array = sort_numbers(test_array)
print(result_sorted_array)
result_string = sort_string(test_string)
result_string_list = result_string.split()
print(result_string_list[0][0] > result_string_list[1][0])
check_list = [result_string_list[ss_number][0] < result_string_list[ss_number + 1][0]
              for ss_number in range(len(result_string_list))
              if (ss_number + 1) < len(result_string_list)]
print(check_list)
test_strings = [test_string for _ in range(20)]
# result_strings = sort_strings_list(test_strings)
# print(result_strings)

