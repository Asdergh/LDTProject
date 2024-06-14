import numpy as np 
import tensorflow as tf 
import pandas as pd 
import json as js 
import os
import openpyxl as xl 
import itertools as it
import matplotlib.pyplot as plt


class ModelCollector:


    def __init__(self, reminder_data_path, turnover_data_path, need_collection,
                 cll_collection):

        self.reminder_data_path = reminder_data_path
        self.turnover_data_path = turnover_data_path
        self.need_collection = need_collection
        self.cll_collection = cll_collection

        self.need_dataframe = pd.read_excel(self.need_collection)
        self.cll_dataframe = pd.read_excel(self.cll_collection)
    
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
                done_condition = False
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

    def collect_data_turnover(self):
    
        indexator = 1
        general_STE_labels = []
        data_collection = {
            "Оборотная ведомость сч. 105": {
                "квартал_1":{},
                "квартал_2": {},
                "квартал_3": {},
                "квартал_4": {}
            },
            "Оборотно-Сальдовая ведомость сч. 21": {
                "квартал_1":{},
                "квартал_2": {},
                "квартал_3": {},
                "квартал_4": {}
            },
            "Оборотно-Сальдовая ведомость сч. 101": {
                "квартал_1":{},
                "квартал_2": {},
                "квартал_3": {},
                "квартал_4": {}
            },
        }

        general_STE_labels = []
        for data_batch_f in os.listdir(self.turnover_data_path):
            
            if indexator > 4:
            
                general_STE_labels = []
                indexator = 1

            curent_batch_f = os.path.join(self.turnover_data_path, data_batch_f)
            curent_dataframe = pd.read_excel(curent_batch_f)

            if "сч. 105" in data_batch_f:

                report_type = "Оборотная ведомость " + "сч. 105"
                STE_labels = curent_dataframe["Наименование нефинансового актива"].to_list()
                STE_labels = self._transform_strings(STE_labels)
                STE_labels, _ = self._sort_strings_list(STE_labels)
                curent_dataframe["Наименование нефинансового актива"] = STE_labels
                curent_dataframe.columns = ["№ п/п", "Инвентарный номенклатурный номер", "Код справочника", "Наименование нефинансового актива",
                                        "Единица измерения", "Остаток на 1 января 2022 г.|дебет|кол-во", 
                                        "Остаток на 1 января 2022 г.|дебет|сумма", "Оборот за 1 квартал 2022 г.|дебет|кол-во", 
                                        "Оборот за 1 квартал 2022 г.|дебет|сумма", "Оборот за 1 квартал 2022 г.|кредит|кол-во", 
                                        "Оборот за 1 квартал 2022 г.|кредит|сумма", "Остаток на 31 марта 2022 г.|дебет|кол-во", 
                                        "Остаток на 31 марта 2022 г.|дебет|сумма"]
            
            elif ("сч. 101" in data_batch_f) or ("сч. 21"  in data_batch_f):

                report_type = "Оборотно-Сальдовая ведомость " + data_batch_f[data_batch_f.find("сч"): data_batch_f.find("за") - 1]
                STE_labels_index = curent_dataframe.columns[0]
                STE_labels = curent_dataframe[STE_labels_index].to_list()
                STE_labels = self._transform_strings(STE_labels)
                STE_labels, _ = self._sort_strings_list(STE_labels)
                curent_dataframe[STE_labels_index] = STE_labels

            general_STE_labels += STE_labels
            
            data_collection[report_type]["general_STE_labels"] = general_STE_labels
            data_collection[report_type][f"квартал_{indexator}"] = {
                "data": curent_dataframe,
                "STE_labels": STE_labels
            }
            general_STE_labels += STE_labels

            indexator += 1

        return data_collection

    def collect_data_reminder(self):

        data_collection = {
            "Ведомость остатков (сч. 105)": {
                "31.03.2022": {},
                "30.06.2022": {},
                "30.09.2022": {},
                "31.12.2022": {}
            },
            "Ведомость остатков (сч. 101)": {
                "31.03.2022": {},
                "30.06.2022": {},
                "30.09.2022": {},
                "31.12.2022": {}
            },
            "Ведомость остатков (сч. 21)": {
                "31.03.2022": {},
                "30.06.2022": {},
                "30.09.2022": {},
                "31.12.2022": {}
            },
        }

        for reminder_sheet_f in os.listdir(self.reminder_data_path):
            
            curent_sample_f = os.path.join(self.reminder_data_path, reminder_sheet_f)
            curent_sample_df = pd.read_excel(curent_sample_f)

            if ("г." not in reminder_sheet_f):
                curent_sample_date = reminder_sheet_f[reminder_sheet_f.find("3"): reminder_sheet_f.find("(") - 1]

            else:
                curent_sample_date = reminder_sheet_f[reminder_sheet_f.find("3"): reminder_sheet_f.find("г.")]

            if "(сч. 105)" in reminder_sheet_f:
                
                report_type = "Ведомость остатков " + reminder_sheet_f[reminder_sheet_f.find("(сч."): reminder_sheet_f.find(")") + 1]
                STE_labels = curent_sample_df["МОЛ"].to_list()
                STE_labels = self._transform_strings(STE_labels)
                STE_labels, _ = self._sort_strings_list(STE_labels)
                curent_sample_df["МОЛ"] = STE_labels

            
            elif ("(сч. 21)" in reminder_sheet_f) or ("(сч. 101)" in reminder_sheet_f):
                
                
                report_type = "Ведомость остатков " + reminder_sheet_f[reminder_sheet_f.find("(сч."): reminder_sheet_f.find(")") + 1]
                "Ведомость остатков " + reminder_sheet_f[reminder_sheet_f.find("(сч."): reminder_sheet_f.find(")") + 1]

                for column in curent_sample_df.columns[3:-4]:
                    
                    del curent_sample_df[column]
                
                del curent_sample_df[curent_sample_df.columns[0]]
                del curent_sample_df[curent_sample_df.columns[0]]

                STE_labels = curent_sample_df[curent_sample_df.columns[0]].to_list()
                STE_labels = self._transform_strings(STE_labels)
                STE_labels, _ = self._sort_strings_list(STE_labels)
                
                curent_sample_df[curent_sample_df.columns[0]] = STE_labels
                #del curent_sample_df[curent_sample_df.columns[0]]
                curent_sample_df.columns = ["Наименование нефинансового актива", "Балансовая стоимость", "Количество", "Сумма амортизации", "Остаточная стоимость"]
            
            data_collection[report_type][curent_sample_date] = {
                "data": curent_sample_df,
                "STE_labels": STE_labels
            }
        
        return data_collection

    def serche_trade_samples(self):

        STE_collection = []
        cn_collection = {}

        for ts_number in range(self.need_dataframe.shape[0]):

            trade_sample = self.need_dataframe.iloc[ts_number]
            cll_dataframe_batch = self.cll_dataframe[(self.cll_dataframe["Реестровый номер в РК"] == trade_sample["Реестровый номер в РК"])
                                            & (self.cll_dataframe["КПГЗ код"] == trade_sample["Конечный код КПГЗ"])
                                            & (self.cll_dataframe["КПГЗ"] == trade_sample["Конечное наименование КПГЗ"])]
            
            trade_sample_STE = cll_dataframe_batch["Название СТЕ"].to_list()
            trade_sample_STE = self._transform_strings(trade_sample_STE)
            trade_sample_STE, sub_cn_collection = self._sort_strings_list(trade_sample_STE)
            

            if len(trade_sample_STE) > 2:

                for variant in trade_sample_STE:

                    STE_collection.append((variant, 
                                        trade_sample["Конечное наименование КПГЗ"], 
                                        sub_cn_collection[variant]))

            elif len(trade_sample_STE) == 1:
                STE_collection.append((trade_sample_STE[0], 
                                    trade_sample["Конечное наименование КПГЗ"], 
                                    sub_cn_collection[trade_sample_STE[0]]))

        return STE_collection


    def combine_result_collection(self, need_path):

        self.STE_collection = self.serche_trade_samples()
        self.data_collection = self.collect_data_turnover()
        self.reminder_data_collection = self.collect_data_reminder()

        self.found_reg_test = {}

        found_con_test = 0
        found_uncon_test = 0

        found_con_rem_test = 0
        found_uncon_rem_test = 0

        time_classification = {
            "квартал_1": "31.03.2022",
            "квартал_2": "30.06.2022",
            "квартал_3": "30.09.2022",
            "квартал_4": "31.12.2022"
        }

        batch_classification = {
            "Оборотная ведомость сч. 105": "Ведомость остатков (сч. 105)",
            "Оборотно-Сальдовая ведомость сч. 101": "Ведомость остатков (сч. 101)",
            "Оборотно-Сальдовая ведомость сч. 21": "Ведомость остатков (сч. 21)"
        }

        for trade_sample in self.STE_collection:

            
            for data_batch in self.data_collection.keys():

                reminder_report_type = batch_classification[data_batch]
                curent_data_batch = self.data_collection[data_batch]
                curent_data_batch_rem = self.reminder_data_collection[reminder_report_type]

                for time_kvartal in curent_data_batch.keys():
                    
                    
                        
                    if time_kvartal != "general_STE_labels":
                            
                        amount_reg = {}
                        reminder_time_kvartal = time_classification[time_kvartal]

                        kvartal_dataframe = curent_data_batch[time_kvartal]["data"]
                        kvartal_dataframe_reminder = curent_data_batch_rem[reminder_time_kvartal]["data"]
                        
                        if data_batch == "Оборотная ведомость сч. 105":

                            serched_dataframe = kvartal_dataframe[kvartal_dataframe["Наименование нефинансового актива"] == trade_sample[0]]
                            serched_dataframe_rem = kvartal_dataframe_reminder[kvartal_dataframe_reminder["МОЛ"] == trade_sample[0]]
                        
                        else:
                            
                            serched_dataframe_amount = kvartal_dataframe[0][kvartal_dataframe[0]["СТЕ"] == trade_sample[0]]
                            serched_dataframe_count = kvartal_dataframe[1][kvartal_dataframe[1]["СТЕ"] == trade_sample[0]]
                            serched_dataframe_rem = kvartal_dataframe_reminder[kvartal_dataframe_reminder["Наименование нефинансового актива"] == trade_sample[0]]

                        desired_condition = False
                        if data_batch == "Оборотная ведомость сч. 105":
                                
                            if serched_dataframe.shape[0] != 0:
                                
                                found_con_test += 1
                                start_amount = serched_dataframe["Остаток на 1 января 2022 г.|дебет|сумма"].to_numpy()[0]
                                start_count = serched_dataframe["Остаток на 1 января 2022 г.|дебет|кол-во"].to_numpy()[0]

                                if np.isnan(start_amount):
                                    
                                    start_amount = serched_dataframe["Оборот за 1 квартал 2022 г.|дебет|сумма"].to_numpy()[0]
                                    start_count = serched_dataframe["Оборот за 1 квартал 2022 г.|дебет|кол-во"].to_numpy()[0]
                                
                                if np.isnan(start_amount) == False or np.isnan(start_count) == False:

                                    desired_condition = True
                                    amount_reg["начальная стоимость"] = str(start_amount)
                                    amount_reg["начальное кол-во"] = str(start_count)
                            
                        else:
                                
                            if serched_dataframe_amount.shape[0] != 0:
                                
                                found_con_test += 1
                                start_amount = serched_dataframe_amount["Сальдо на начало периода|дебет|сумма"].to_numpy()[0]
                                start_count = serched_dataframe_count["Сальдо на начало периода|дебет|кол."].to_numpy()[0]

                                if np.isnan(start_amount) == False or np.isnan(start_count) == False:
                                    
                                    desired_condition = True
                                    amount_reg["начальная стоимость"] = str(start_amount)
                                    amount_reg["начальное кол-во"] = str(start_count)
                                
                                
                        if data_batch == "Оборотная ведомость сч. 105":
                                
                            
                            if serched_dataframe_rem.shape[0] != 0:
                                
                                found_con_rem_test += 1
                                end_amount = serched_dataframe_rem["Сумма"].to_numpy()[0]
                                end_count = serched_dataframe_rem["Количество"].to_numpy()[0]

                                if np.isnan(end_amount):
                                    end_amount = serched_dataframe["Остаток на 31 марта 2022 г.|дебет|сумма"].numpy()[0]  
                                    
                                if np.isnan(end_amount) == False or np.isnan(end_count) == False:
                                    
                                    desired_condition = True
                                    amount_reg["конечная стоимость"] = str(end_amount)
                                    amount_reg["конечное кол-во"] = str(end_count)
                            
                        else:
                            
                            if serched_dataframe_rem.shape[0] != 0:
                                
                                found_con_rem_test += 1
                                end_amount = serched_dataframe_rem["Остаточная стоимость"].to_numpy()[0]
                                end_count = serched_dataframe_rem["Количество"].to_numpy()[0]

                                if end_amount == 0:
                                    end_amount = serched_dataframe_rem["Балансовая стоимость"].to_numpy()[0]
                                
                                if (np.isnan(end_amount) == False) or (np.isnan(end_count) == False):
                                    
                                    desired_condition = True
                                    amount_reg["конечная стоимость"] = str(end_amount)
                                    amount_reg["конечное кол-во"] = str(end_count)
                                
                                
        
                            elif serched_dataframe.shape[0] != 0:

                                found_uncon_rem_test += 1
                                if data_batch == "Оборотная ведомость сч. 105":

                                    end_amount = serched_dataframe["Остаток на 31 марта 2022 г.|дебет|сумма"].to_numpy()[0]
                                    end_count = serched_dataframe["Остаток на 31 марта 2022 г.|дебет|кол-во"].to_numpy()[0]
                                        
                                    if np.isnan(end_amount) == False or np.isnan(end_count) == False:

                                        desired_condition = True
                                        amount_reg["конечная стоимость"] = str(end_amount)
                                        amount_reg["конечное кол-во"] = str(end_count)
                            
                            

                        if desired_condition:
                            
                            if "начальная стоимость" in amount_reg.keys() and "начальное кол-во" in amount_reg.keys():

                                if "конечная стоимость" not in amount_reg.keys():
                                    amount_reg["конечная стоимость"] = "0.0"

                                if "конечное кол-во" not in amount_reg.keys():
                                    amount_reg["конечное кол-во"] = "0.0"

                                self.found_reg_test[trade_sample[2]] = {}
                                self.found_reg_test[trade_sample[2]]["тип ведомости"] = data_batch
                                self.found_reg_test[trade_sample[2]]["Классификация"] = trade_sample[1]
                                self.found_reg_test[trade_sample[2]][time_kvartal] = amount_reg

        with open(need_path, "w") as json_file:
            js.dump(self.found_reg_test, json_file)
    
    def formulate_data(self, ts_collection_path):

        data_collection = {}
        with open(ts_collection_path, "r") as json_file:

            dataset = js.load(json_file)
            cll_types = [dataset[trade_sample]["Классификация"] for trade_sample in dataset]
            
            for cll_type in cll_types:
                
                sub_collection = {}
                sub_collection["кол-во начало"] = []
                sub_collection["сумма начало"] = []
                sub_collection["название"] = []
                sub_collection["кол-во конец"] = []
                sub_collection["сумма конец"] = []

                for trade_sample in dataset.keys():

                    if dataset[trade_sample]["Классификация"] == cll_type:

                        sub_collection["название"].append(trade_sample)
                        for kvartal in dataset[trade_sample].keys():

                            if kvartal not in["тип ведомости", "Классификация"]:
                                
                                kvartal_sample = dataset[trade_sample][kvartal]
                                sub_collection["кол-во начало"].append(float(kvartal_sample["начальное кол-во"]))
                                sub_collection["кол-во конец"].append(float(kvartal_sample["конечное кол-во"]))
                                sub_collection["сумма начало"].append(float(kvartal_sample["начальная стоимость"]))
                                sub_collection["сумма конец"].append(float(kvartal_sample["конечная стоимость"]))
                
                        data_collection[cll_type] = sub_collection
        
        return data_collection


