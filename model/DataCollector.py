import numpy as np 
import tensorflow as tf 
import pandas as pd 
import json as js 
import os
import openpyxl as xl 
import itertools as it
import matplotlib.pyplot as plt
import random as rd
import seaborn as sb
from StringPreprocessor import StringPreprocessor


class DataCollector(StringPreprocessor):

    def __init__(self, trade_info_path, turnover_data_path, reminder_data_path,
                 cll_data_path):

        self.trade_info_path = trade_info_path
        self.turnover_data_path = turnover_data_path
        self.reminder_data_path = reminder_data_path

        self.trade_inf_dataframe = pd.read_excel(trade_info_path)
        self.cll_dataframe = pd.read_excel(cll_data_path)
    
    def collect_data_turnover(self, data_path):
    
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
        for data_batch_f in os.listdir(data_path):
            
            if indexator > 4:
            
                general_STE_labels = []
                indexator = 1

            curent_batch_f = os.path.join(data_path, data_batch_f)
            curent_dataframe = pd.read_excel(curent_batch_f)

            if "сч. 105" in data_batch_f:

                report_type = "Оборотная ведомость " + "сч. 105"
                STE_labels = curent_dataframe["Наименование нефинансового актива"].to_list()
                STE_labels = self._transform_string_list(STE_labels)
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
    

    def correct_turnover_databatch(self, data_collection):
        
        for data_batch in data_collection.keys():

            if data_batch != "Оборотная ведомость сч. 105":

                curent_data_batch = data_collection[data_batch]
                for time_kvartal in curent_data_batch.keys():

                    if time_kvartal != "general_STE_labels":

                        curent_dataframe = curent_data_batch[time_kvartal]["data"]
                        for column in curent_dataframe.columns:

                            if (column in ['ГОСУДАРСТВЕННОЕ КАЗЕННОЕ УЧРЕЖДЕНИЕ ГОРОДА МОСКВЫ "ИНФОРМАЦИОННЫЙ ГОРОД"', 
                                "Unnamed: 4", "Unnamed: 10", "Unnamed: 14", "Unnamed: 9", "Unnamed: 12"]) == False:
                                del curent_dataframe[column]

                        curent_dataframe.columns = ["СТЕ", "Код", "Определитель", "Сальдо на начало периода|дебет", "Обороты за период|дебет", "Сальдо на конец периода|дебет"]
                        amount_dataframe = curent_dataframe[curent_dataframe["Определитель"] == "Сумма"]
                        count_dataframe = curent_dataframe[curent_dataframe["Определитель"] == "Кол."]

                        del amount_dataframe["Определитель"]
                        amount_dataframe.columns = ["СТЕ", "Код", "Сальдо на начало периода|дебет|сумма","Обороты за период|дебет|сумма", "Сальдо на конец периода|дебет|сумма"]
                        
                        del count_dataframe["Определитель"]
                        count_dataframe.columns = ["СТЕ", "Код", "Сальдо на начало периода|дебет|кол.", "Обороты за период|дебет|кол.", "Сальдо на конец периода|дебет|кол."]
                        count_dataframe["СТЕ"] = amount_dataframe["СТЕ"].to_list()
                        count_dataframe["Код"] = amount_dataframe["Код"].to_list()

                        data_collection[data_batch][time_kvartal]["data"] = [amount_dataframe, count_dataframe]

        return data_collection
    
    def collect_data_reminder(self, data_path):

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

        for reminder_sheet_f in os.listdir(data_path):
            
            curent_sample_f = os.path.join(data_path, reminder_sheet_f)
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
                curent_sample_df.columns = ["Наименование нефинансового актива", "Цена", "Количество", "Сумма"]
            
            elif ("(сч. 21)" in reminder_sheet_f) or ("(сч. 101)" in reminder_sheet_f):
                
                
                report_type = "Ведомость остатков " + reminder_sheet_f[reminder_sheet_f.find("(сч."): reminder_sheet_f.find(")") + 1]
                "Ведомость остатков " + reminder_sheet_f[reminder_sheet_f.find("(сч."): reminder_sheet_f.find(")") + 1]

                for column in curent_sample_df.columns[3:-4]:
                    
                    del curent_sample_df[column]
                
                del curent_sample_df[curent_sample_df.columns[0]]
                del curent_sample_df[curent_sample_df.columns[0]]

                STE_labels = curent_sample_df[curent_sample_df.columns[0]].to_list()
                STE_labels =self._transform_strings(STE_labels)
                STE_labels, _ = self._sort_strings_list(STE_labels)
                
                curent_sample_df[curent_sample_df.columns[0]] = STE_labels
                #del curent_sample_df[curent_sample_df.columns[0]]
                curent_sample_df.columns = ["Наименование нефинансового актива", "Балансовая стоимость", "Количество", "Сумма амортизации", "Остаточная стоимость"]
            
            data_collection[report_type][curent_sample_date] = {
                "data": curent_sample_df,
                "STE_labels": STE_labels
            }
        
        return data_collection


    def collect_trade_samples(self):

        STE_collection = []
        for ts_number in range(self.trade_inf_dataframe.shape[0]):

            trade_sample = self.trade_inf_dataframe.iloc[ts_number]
            self.cll_dataframe_batch = self.cll_dataframe[(self.cll_dataframe["Реестровый номер в РК"] == trade_sample["Реестровый номер в РК"])
                                            & (self.cll_dataframe["КПГЗ код"] == trade_sample["Конечный код КПГЗ"])
                                            & (self.cll_dataframe["КПГЗ"] == trade_sample["Конечное наименование КПГЗ"])]
            
            trade_sample_STE = self.cll_dataframe_batch["Название СТЕ"].to_list()
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
    
    def collect_general_samples(self):

        general_STE_collection = []
        for cll_cell in range(self.cll_dataframe.shape[0]):

            curent_trade_sample = self.cll_dataframe.iloc[cll_cell]
            STE_label = curent_trade_sample["Название СТЕ"]
            if type(STE_label) != float:

                STE_label = self._transform_single_string(STE_label)
                STE_label_sorted, STE_label = self._sort_single_string(STE_label)
                cll_type = curent_trade_sample["КПГЗ"]
                
                general_STE_collection.append((STE_label_sorted, cll_type, STE_label))
    


    def generate_all_collections(self):

        self.data_collection = self.collect_data_turnover(self.turnover_data_path)
        self.data_collection = self.correct_turnover_databatch()
        self.reminder_data_collection = self.collect_data_reminder(self.reminder_data_path)

        self.trade_samples = self.collect_trade_samples()
        self.general_samples = self.collect_general_samples()



    def combine_data_from_collections(self, STE_samples, json_file_path=None):
        
        found_reg_test = {}
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

        for trade_sample in STE_samples:

            found_reg_test[trade_sample[2]] = {}
            for data_batch in self.data_collection.keys():

                reminder_report_type = batch_classification[data_batch]
                curent_data_batch = self.data_collection[data_batch]
                curent_data_batch_rem = self.reminder_data_collection[reminder_report_type]
                found_reg_test[trade_sample[2]]["кварталы"] = {}

                for time_kvartal in self.data_collection[data_batch].keys():
                    
                    if time_kvartal != "general_STE_labels":
                        
                        inv_time_kvartal = time_classification[time_kvartal]
                        if data_batch == "Оборотная ведомость сч. 105":

                            curent_dataframe = curent_data_batch[time_kvartal]["data"]
                            curent_dataframe_rem = curent_data_batch_rem[inv_time_kvartal]["data"]
                        
                        else:

                            curent_dataframe_amount = curent_data_batch[time_kvartal]["data"][0]
                            curent_dataframe_count = curent_data_batch[time_kvartal]["data"][1]
                            curent_dataframe_rem = curent_data_batch_rem[inv_time_kvartal]["data"]
                    

                        if data_batch == "Оборотная ведомость сч. 105":

                            amount_reg = {}
                            serched_dataframe = curent_dataframe[curent_dataframe["Наименование нефинансового актива"] == trade_sample[0]]
                            serched_dataframe_rem = curent_dataframe_rem[curent_dataframe_rem["Наименование нефинансового актива"] == trade_sample[0]]
                            if serched_dataframe.shape[0] != 0:
                                
                                start_amount = serched_dataframe["Остаток на 1 января 2022 г.|дебет|сумма"].to_numpy()[0]
                                start_count = serched_dataframe["Остаток на 1 января 2022 г.|дебет|кол-во"].to_numpy()[0]

                                if np.isnan(start_amount) == True or np.isnan(start_count) == True:
                                    
                                    start_amount = serched_dataframe["Оборот за 1 квартал 2022 г.|дебет|сумма"].to_numpy()[0]
                                    start_count = serched_dataframe["Оборот за 1 квартал 2022 г.|дебет|кол-во"].to_numpy()[0]

                                amount_reg["начальная стоимость"] = start_amount
                                amount_reg["начальное кол-во"] = start_count
                                

                            if serched_dataframe_rem.shape[0] != 0:
                                
                                end_amount = serched_dataframe_rem["Сумма"].to_numpy()[0]
                                end_count = serched_dataframe_rem["Количество"].to_numpy()[0]

                                amount_reg["конечная стоимость"] = end_amount
                                amount_reg["конечное кол-во"] = end_count

                            if len(amount_reg) != 0:
                                
                                found_reg_test[trade_sample[2]]["Классификация"] = trade_sample[1]
                                found_reg_test[trade_sample[2]]["тип ведомости"] = data_batch
                                found_reg_test[trade_sample[2]]["кварталы"][time_kvartal] = amount_reg
                        
                        else:
                            
                            amount_reg = {}
                            serched_dataframe_amount = curent_dataframe_amount[curent_dataframe_amount["СТЕ"] == trade_sample[0]]
                            serched_dataframe_count = curent_dataframe_count[curent_dataframe_count["СТЕ"] == trade_sample[0]]
                            serched_dataframe_rem = curent_dataframe_rem[curent_dataframe_rem["Наименование нефинансового актива"] == trade_sample[0]]
                            
                            if serched_dataframe_amount.shape[0] != 0:

                                start_amount = serched_dataframe_amount["Сальдо на начало периода|дебет|сумма"].to_numpy()[0]
                                start_count = serched_dataframe_count["Сальдо на начало периода|дебет|кол."].to_numpy()[0]

                                if np.isnan(start_amount) == True or np.isnan(start_count) == True:
                                    
                                    start_amount = serched_dataframe_amount["Обороты за период|дебет|сумма"].to_numpy()[0]
                                    start_count = serched_dataframe_count["Обороты за период|дебет|кол."].to_numpy()[0]
                                
                                
                                amount_reg["начальная стоимость"] = start_amount
                                amount_reg["начальное кол-во"] = start_count
                            
                            if serched_dataframe_rem.shape[0] != 0:
                                
                                end_amount = serched_dataframe_rem["Балансовая стоимость"].to_numpy()[0]
                                end_count = serched_dataframe_rem["Количество"].to_numpy()[0]

                                amount_reg["конечная стоимость"] = end_amount
                                amount_reg["конечное кол-во"] = end_count
                            
                            if len(amount_reg) != 0:
                                
                                found_reg_test[trade_sample[2]]["Классификация"] = trade_sample[1]
                                found_reg_test[trade_sample[2]]["тип ведомости"] = data_batch
                                found_reg_test[trade_sample[2]]["кварталы"][time_kvartal] = amount_reg

        collection_without_empty = {}
        for trade_sample in found_reg_test.keys():

            if len(found_reg_test[trade_sample]["кварталы"]) != 0:
                collection_without_empty[trade_sample] = found_reg_test[trade_sample]
        
        collection_without_nan = {}
        for trade_sample in collection_without_empty.keys():

            curent_trade_sample = collection_without_empty[trade_sample]
            trade_sample_keys = [str(ts_key) for ts_key in curent_trade_sample.keys()]
            if "NaN" not in trade_sample_keys:

                collection_without_nan[trade_sample] = curent_trade_sample


        if json_file_path is not None:
            with open(json_file_path, "w") as json_file:

                js.dump(collection_without_nan, json_file)

        return collection_without_nan
    

    def formulate_data(self, trade_collection):

        all_types = [trade_collection[trade_sample]["Классификация"] for trade_sample in trade_collection.keys()]
        likvid_collection = {}
        for cll_type in all_types:

            likvid_collection[cll_type] = {}

            for trade_sample in trade_collection.keys():
                
                likvid_collection[cll_type][trade_sample] = {}
                ts_curent = trade_collection[trade_sample]
                curent_sample = trade_collection[trade_sample]["кварталы"]

                for time_kvartal in curent_sample.keys():

                    kvartal_reg = curent_sample[time_kvartal]
                    kvartal_reg_keys = [reg_key for reg_key in kvartal_reg.keys()]

                    if cll_type == ts_curent["Классификация"]:
                        
                        if ("конечная стоимость" in kvartal_reg_keys) and ("конечное кол-во" in kvartal_reg_keys):

                            likvid_collection[cll_type][trade_sample][time_kvartal] = kvartal_reg


        collection_without_empty = {}
        for cll_sample in likvid_collection.keys():

            curent_cll_sample = likvid_collection[cll_sample]
            collection_without_empty[cll_sample] = {}
            for trade_sample in curent_cll_sample.keys():

                if len(curent_cll_sample[trade_sample]) != 0:

                    collection_without_empty[cll_sample][trade_sample] = curent_cll_sample[trade_sample]

        collection_without_duplicates = {}
        deprecated_keys = []
        for cll_cell in collection_without_empty.keys():

            curent_cell = collection_without_empty[cll_cell]
            collection_without_duplicates[cll_cell] = {}

            for trade_sample in curent_cell.keys():

                if trade_sample not in deprecated_keys:

                    collection_without_duplicates[cll_cell][trade_sample] = curent_cell[trade_sample]
                    deprecated_keys.append(trade_sample)
                
        return collection_without_duplicates


    def make_final_collections(self):

        self.trade_samples_collection = self.combine_data_from_collection(STE_samples=self.trade_samples)
        self.general_samples_collection = self.combine_data_from_collection(STE_samples=self.general_samples)



