class StringPreprocession:

    def __init__(self):
        pass
    
    def _transform_strings(self, strings_list):

        result_STE_labels = strings_list
        allowed_simbols = "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮйцукенгшщзхъфывапролджэячсмитьбюQWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm12345467890"

        for (label_number, STE_label) in enumerate(strings_list):

            tmp_STE_label = ""
            if (type(STE_label) != float):

                for simbol in STE_label:
                            
                    if (simbol in allowed_simbols):
                        tmp_STE_label += simbol.lower()

                    else:
                        tmp_STE_label += " "
                    
                tmp_STE_list = tmp_STE_label.split()
                result_STE_list = []
                iterator = 0
                while iterator < len(tmp_STE_list):

                    sub_string = tmp_STE_list[iterator]
                    delete_condition = False
                    if len(sub_string) >= 4:

                        for simbol in sub_string:

                            if (simbol in "1234567890"):

                                delete_condition = True
                                break

                        if not delete_condition:
                            result_STE_list.append(sub_string)
                    
                    iterator += 1
                
                result_STE_label = " ".join(sub_string for sub_string in result_STE_list)     
                result_STE_labels[label_number] = result_STE_label
                    
            else:
                result_STE_labels[label_number] = STE_label
        
        return result_STE_labels

    def _sort_strings_list(self, strings_list):

        result_strings_list = []
        cn_collection = {}
        
        for string in strings_list:
            
            if (type(string) != float):

                tmp_string_list = string.split()
                curent_list_part = 1
                while curent_list_part < len(tmp_string_list):

                    for sub_string_number in range(len(tmp_string_list) - curent_list_part):

                        if (tmp_string_list[sub_string_number] > tmp_string_list[sub_string_number + 1]):
                            
                            tmp_string_list[sub_string_number], tmp_string_list[sub_string_number + 1] = \
                            tmp_string_list[sub_string_number + 1], tmp_string_list[sub_string_number]

                    curent_list_part += 1

                result_string = " ".join(sub_string for sub_string in tmp_string_list)
                result_strings_list.append(result_string)
                cn_collection[result_string] = string
            
            else:
                result_strings_list.append(string)
                cn_collection[string] = string
        
        return (result_strings_list, cn_collection)


    def _transform_single_string(self, string_to_transform):

        allowed_simbols = "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮйцукенгшщзхъфывапролджэячсмитьбюQWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm12345467890"
        tmp_STE_label = ""
        if (type(string_to_transform) != float):

            for simbol in string_to_transform:
                            
                if (simbol in allowed_simbols):
                    tmp_STE_label += simbol.lower()

                else:
                    tmp_STE_label += " "
                    
            tmp_STE_list = tmp_STE_label.split()
            result_STE_list = []
            iterator = 0
            while iterator < len(tmp_STE_list):

                sub_string = tmp_STE_list[iterator]
                delete_condition = False
                if len(sub_string) >= 4:

                    for simbol in sub_string:

                        if (simbol in "1234567890"):

                            delete_condition = True
                            break

                    if not delete_condition:
                        result_STE_list.append(sub_string)
                    
                iterator += 1
            
            result_STE_label = " ".join(sub_string for sub_string in result_STE_list)
            return result_STE_label


    def _sort_single_string(self, string_to_sort):

        tmp_string_list = string_to_sort.split()
        curent_list_part = 1
        while curent_list_part < len(tmp_string_list):

            for sub_string_number in range(len(tmp_string_list) - curent_list_part):

                if (tmp_string_list[sub_string_number] > tmp_string_list[sub_string_number + 1]):
                            
                        tmp_string_list[sub_string_number], tmp_string_list[sub_string_number + 1] = \
                        tmp_string_list[sub_string_number + 1], tmp_string_list[sub_string_number]

                curent_list_part += 1

        result_string = " ".join(sub_string for sub_string in tmp_string_list)
        return (result_string, string_to_sort)
