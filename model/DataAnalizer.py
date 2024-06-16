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
from DataCollector import DataCollector


class DataAnalizer(DataCollector):

    def __init__(self, trade_info_path, turnover_data_path, reminder_data_path,
                 cll_data_path):

        supper().__init__(trade_info_path, turnover_data_path, reminder_data_path,
                 cll_data_path)

    def generate_dataset(self, trade_collection, need_data_shape, 
                         time_kvartal, test_data=False):

        time_kvartals = {
            "квартал_1": 0,
            "квартал_2": 1,
            "квартал_3": 2,
            "квартал_4": 3 
        }
        dataset_tensor = np.zeros(need_data_shape)
        curent_data_tensor = []
        dataset_labels = []
        curent_sample_number = 0
        for cll_cell_id in trade_collection.keys():

            curent_cll_cell = trade_collection[cll_cell_id]
            for trade_sample in curent_cll_cell.keys():

                
                features = [[float(curent_cll_cell[trade_sample][time_kvartal][feature]) 
                        for feature in curent_cll_cell[trade_sample][time_kvartal].keys()]
                        for time_kvartal in curent_cll_cell[trade_sample].keys()]
                
                if time_kvartal == "all":
                    
                    dataset_labels.append(trade_sample)
                    feature_tensor = np.asarray(features)
                    feature_tensor = np.asarray([np.mean(feature_tensor[:, col_number]) for col_number in range(feature_tensor.shape[1])])
                    curent_data_tensor.append(feature_tensor)
                
                else:
                    
                    if time_kvartals[time_kvartal] < len(features):
                        
                        dataset_labels.append(trade_sample)
                        feature_tensor = features[time_kvartals[time_kvartal]]
                        curent_data_tensor.append(feature_tensor)

                curent_sample_number += 1
        
        

        if (need_data_shape[0] < dataset_tensor.shape[0]) or (need_data_shape[1] < dataset_tensor.shape[1]):

            raise BaseException("dimention that was choosed less then dataset_tensor")

        else:
            
        
            curent_data_tensor = np.asarray(curent_data_tensor)
            if test_data:
                dataset_tensor = np.resize(dataset_tensor, (curent_data_tensor.shape[0], need_data_shape[1]))
            dataset_tensor[:curent_data_tensor.shape[0], :curent_data_tensor.shape[1]] = curent_data_tensor
            dataset_tensor_std = (dataset_tensor - np.mean(dataset_tensor)) / np.std(dataset_tensor)
            dataset_tensor_std += np.random.normal(0.12, 1.67, dataset_tensor.shape)
            
        return (dataset_tensor_std, dataset_labels)

    def build_reg_model(self, need_feature_shape):

        input_tensor = tf.keras.Input(shape=(need_feature_shape, ))

        model_layer = tf.keras.layers.Dense(120, activation="relu")(input_tensor)
        model_layer = tf.keras.layers.Dense(64, activation="relu")(model_layer)
        model_layer = tf.keras.layers.Dense(32, activation="relu")(model_layer)
        model_layer = tf.keras.layers.Dense(1, activation="linear")(model_layer)

        model = tf.keras.Model(input_tensor, model_layer)
        model.compile(
            optimizer=tf.keras.optimizers.RMSprop(learning_rate=0.001),
            loss=tf.keras.losses.MeanSquaredError(),
            metrics=[tf.keras.metrics.MeanAbsoluteError()]
        )

        return model

    def fit_model(self, train_dataset_tensor, train_dataset_labels):


        self.regression_model = self.build_reg_model(need_feature_shape=train_dataset_tensor.shape[1])
        self.reg_model_history = self.regression_model.fit(train_dataset_tensor, train_dataset_labels,
                                           epochs=100,
                                           batch_size=60)
    
    def show_stat(self, data_to_analize, graph_type):

        model_predictions = self.regression_model.predict(data_to_analize[0])
        model_predictions = np.resize(model_predictions, (model_predictions.shape[0], ))
        
        plt.style.use("dark_background")
        fig, axis = plt.subplots()

        if graph_type == "hist":
            
            print(len(data_to_analize[1]), model_predictions.shape)
            axis.hist(model_predictions, bins=len(data_to_analize[1]), color="orange")
            axis.set_xticklabels(data_to_analize[1])
            axis.grid(True)

            plt.xticks(rotation=60, ha='right')
            plt.show()
        
        elif graph_type == "heatmap":
            
            columns = []
            heatmap = np.zeros((len(data_to_analize[1]), model_predictions.shape[0]))
            for (row_number, ste_label) in enumerate(data_to_analize[1]):
                for (col_number, prediction) in enumerate(model_predictions):
                    
                    if row_number == col_number:
                        heatmap[row_number, col_number] = prediction
                        columns.append(f"Prediction_{row_number}")
                        
            heatmap_df = pd.DataFrame(data=heatmap,
                                    index=data_to_analize[1],
                                    columns=columns)
            sb.heatmap(heatmap_df, cmap="magma", linewidth=.5)
        
        elif graph_type == "corr":
            
            corr_heatmap = np.cov(data_to_analize[0])
            corr_heatmap_df = pd.DataFrame(data=corr_heatmap,
                                        index=data_to_analize[1],
                                        columns=data_to_analize[1])
            sb.heatmap(corr_heatmap_df, linewidth=.5)


    def formulate_final_json(self, samples, file_path):
    
        final_json = {
            "Id": "None",
            "CustomerId": "None",
            "СПГЗ": {}
        }

        cll_STE_labels = self.cll_dataframe["Название СТЕ"]
        cll_STE_labels = self._transform_strings(cll_STE_labels)
        self.cll_dataframe["Название СТЕ"] = cll_STE_labels

        for sample_key in samples:


            serched_dataframe = self.cll_dataframe[self.cll_dataframe["Название СТЕ"] == sample_key]
            if serched_dataframe.shape[0] != 1:
                sample = serched_dataframe.sample()

                if serched_dataframe.shape[0] != 0:

                    final_json["СПГЗ"][sample_key] = {
                        "наименоениве товара": str(sample["Название СТЕ"].to_list()[0]),
                        "наименование характеристик": str(sample["наименование характеристик"].to_list()[0]),
                        "КПГЗ код": str(sample["КПГЗ код"].to_list()[0]),
                        "КПГЗ": str(sample["КПГЗ"].to_list()[0]),
                        "СПГЗ код": str(sample["СПГЗ код"].to_list()[0]),
                        "Реестровый номер в РК": str(sample["Реестровый номер в РК"].to_list()[0])
                    }

            else:

                if serched_dataframe.shape[0] != 0:

                    final_json["СПГЗ"][sample_key] = {
                        "наименоениве товара": str(serched_dataframe["Название СТЕ"].to_list()[0]),
                        "наименование характеристик": str(serched_dataframe["наименование характеристик"].to_list()[0]),
                        "КПГЗ код": str(serched_dataframe["КПГЗ код"].to_list()[0]),
                        "КПГЗ": str(serched_dataframe["КПГЗ"].to_list()[0]),
                        "СПГЗ код": str(serched_dataframe["СПГЗ код"].to_list()[0]),
                        "Реестровый номер в РК": str(serched_dataframe["Реестровый номер в РК"].to_list()[0])
                    }

        with open(file_path, "w") as json_file:

            js.dump(final_json, json_file)
