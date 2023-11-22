import numpy as np
import pandas as pd
import glob
from netCDF4 import Dataset
import sys
import os
import datetime

#from fake_model import fake_mod

def compute_objective(exp_dir,num_parts,num_params,positions):
    #np.random.seed(1)
    objective_output = np.zeros(num_parts)
    o_file = exp_dir+'/run/output.txt'
    
    ##### THINGS TO BE MANUALLY EDITED #####
    flux_et = pd.read_csv(
        '/discover/nobackup/trobinet/pso/step_3_process_fluxcom/outputs/' +
        'le_truth_fluxcom_rs_meteo_ensemble_watts_per_m2_2001-01-01_2009-12-31_selected_tiles.csv'
    )
    start = datetime.date(2001,1,1)
    end = datetime.date(2009,12,31)
    #########################################
    
    curr = start
    delta = datetime.timedelta(days=1)
    flux_et = flux_et.drop('time',axis=1)
    flux_et = np.array(flux_et)
    flux_et = flux_et[:,1:]

    # get index where we have flux ET measurements;
    # only perform the objective calculation at these locations
    idx = np.where(flux_et != -9999)

    # get shaes for later and initialize
    num_times, num_pixels = np.shape(flux_et)
    model_et = np.zeros(num_times)
    model_trns = np.zeros(num_times)
    for ens in range(num_parts):
        model_et_all = np.zeros((num_times,num_pixels))
        model_trns_all = np.zeros((num_times,num_pixels))
        time = 0
        root = os.path.join(
            exp_dir,
            '../',
            str(ens),
            'output/SMAP_EASEv2_M36/cat/ens0000'
        )
        #ens_form = 'e0000'
        #files = sorted(glob.glob(root+'/**/**/*.nc4'))
        while (curr<=end):
            curr_str = curr.strftime("%Y%m%d")
            curr_yr = curr.strftime("%Y")
            curr_mon = curr.strftime("%m")
            this_file = os.path.join(
                root,
                'Y'+curr_yr,
                'M'+curr_mon,
                str(ens) + '.tavg24_1d_lnd_Nt.'+curr_str+'_1200z.nc4'
            )
            # get the model data necesarry
            data = Dataset(this_file,mode='r')
            model_et_date = np.array(data['LHLAND'][:]) #will already be in ascending pixel order by default 
            model_trns_date = np.array(data['EVPTRNS'][:])
            #model_et_date_neg = np.where(model_et_date < 0)
            #model_et_date[model_et_date_neg] = 0
            #model_et_date = -model_et_date
            model_et_all[time,:] = model_et_date
            model_trns_all[time,:] = model_trns_date
            time += 1
            curr += delta
        curr = start
        #lux_et = np.random.rand(num_times,num_pixels)
        #odel_et_all = positions
        #model_et_all,flux_et = fake_mod(num_times,num_pixels,positions,ens)
        idx_2 = np.where((model_et_all > 0) & (flux_et > 0))
        model_obj = model_et_all[idx_2]
        flux_obj = flux_et[idx_2]
        model_trns_obj = model_trns_all[idx_2]
        curr_obj_val = np.sqrt(((model_et_all[idx_2] - flux_et[idx_2]) ** 2).mean())
        with open(o_file,'a') as f:
            #f.write(str('files'))
            #f.write('\n')
            #f.write(str(files))
            #f.write('\n')
            #f.write(str('model_et_all'))
            #f.write('\n')
            #f.write(str(model_et_all))
            #f.write('\n')
            #f.write(str('flux_et'))
            #f.write('\n')
            #f.write(str(flux_et))
            #f.write('\n')
            f.write(str('model_obj[-10:]'))
            f.write('\n')
            f.write(str(model_obj[-10:]))
            f.write('\n')
            f.write(str('flux_obj[-10:]'))
            f.write('\n')
            f.write(str(flux_obj[-10:]))
            f.write('\n')
            f.write(str('np.shape(model_obj)'))
            f.write('\n')
            f.write(str(np.shape(model_obj)))
            f.write('\n')
            f.write('str(np.shape(flux_obj))')
            f.write('\n')
            f.write(str(np.shape(flux_obj)))
            f.write('\n')
            f.write(str(model_trns_obj[-10:]))
            f.write('\n')
        #assign to array to be returned
        objective_output[ens] = curr_obj_val
    return objective_output