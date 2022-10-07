import logging
import pandas as pd 
from functools import reduce
import numpy as np 

def configure_vpp(self):
    """_summary_

    Returns:
        _type_: _description_
    """    
    # list to concat all dfs later on
    asset_frames_total = []
    asset_frames_FCR = []
    # for each asset type defined in the config (e.g.: "hydro", "wind")
    for asset_type in self.config["assets"].keys():
        # for every plant configuration there is per asset type
        for plant_config in range(len(self.config["assets"][asset_type])):
            # get the qunatity of plants
            quantity = self.config["assets"][asset_type][plant_config]["quantity"]
            # get the maximum capacity of these plants 
            max_capacity_MW = self.config["assets"][asset_type][plant_config]["max_capacity_MW"]
            max_FCR_capacity_share = self.config["assets"][asset_type][plant_config]["max_FCR_capacity_share"]
            # get the name of the column in the renewables csv
            asset_column_names = self.config["assets"][asset_type][plant_config]["asset_column_names"]
            # initialize a array with zeros and the length of the renewables dataframe
            total_asset_capacity = np.array([0.0] * len(self.renewables_df))
            total_asset_FCR_capacity = np.array([0.0] * len(self.renewables_df))

            i = 1
            while i < quantity: 
                for asset_column_name in (asset_column_names):
                    asset_data = self.renewables_df[[asset_column_name]].values.flatten()
                    asset_data *= max_capacity_MW
                    asset_FCR_capacity = asset_data * max_FCR_capacity_share
                    
                    total_asset_FCR_capacity += asset_FCR_capacity 
                    total_asset_capacity += asset_data
                    
                    i += 1
                    if i < quantity:
                        continue
                    else: 
                        break                        
                
            total_df = pd.DataFrame(index=self.renewables_df.index)
            FCR_df = pd.DataFrame(index=self.renewables_df.index)
            
            total_df[asset_type + "_class_" + str(plant_config)] = total_asset_capacity
            FCR_df[asset_type + "_class_" + str(plant_config)] = total_asset_FCR_capacity
            asset_frames_total.append(total_df)
            asset_frames_FCR.append(FCR_df)

    if not asset_frames_total: 
        logging.error("No asset data found")
    all_asset_data = reduce(lambda x, y: pd.merge(x, y, on = "time"), asset_frames_total)
    all_asset_data_FCR = reduce(lambda x, y: pd.merge(x, y, on = "time"), asset_frames_FCR)

    all_asset_data['Total'] = all_asset_data.iloc[:,:].sum(axis=1)
    all_asset_data_FCR['Total'] = all_asset_data_FCR.iloc[:,:].sum(axis=1)
    
    return all_asset_data, all_asset_data_FCR
    
    
       
def simulate_vpp(self):
    """_summary_
    """    
    vpp_total = self.asset_data_total[str(self.market_start) : str(self.market_end)].to_numpy(dtype=np.float32)
    #vpp_total_FCR = self.asset_data_FCR_total[str(self.market_start) : str(self.market_end)].to_numpy(dtype=np.float32)
    
    self.activation_results["vpp_total"] = vpp_total
    #self.activation_results["vpp_total_FCR"] = vpp_total_FCR
    self.activation_results["bid_sizes_all_slots"] = [0] * 96
    