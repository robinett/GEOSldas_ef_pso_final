# script that will run the PSO algorithm

#activate conda environment

# import libraries
from os.path import exists
import pandas as pd
import numpy as np
import os
import glob
from netCDF4 import Dataset
import sys
from compute_objective_v2 import compute_objective
import shutil
import tarfile

exp_dir = sys.argv[1]

# set important parameters
from_restart = False
pso_restart_dir = '/discover/nobackup/trobinet/pso_restarts/GEOSldas_CN45_ens_ind_2003_2006'
convergence_threshold = 5 #num iterations with no change to global_best to converge
max_iterations = 1000
restart_every = 1
nparticles = 10
nparameters = 10
spinup_iterations = 0
o_file = os.path.join(exp_dir,'run/output.txt')
#parameter 1: aj in g1 EF for forests
#parameter 2: aj in g1 EF for croplands
#parameter 3: aj in g1 EF for grasslands
#parameter 4: aj in g1 EF for savannas
#parameter 5: aj in g1 EF for shrublands
#parameter 6: alpha in Ksat EF
#parameter 7: beta in Ksat EF
#parameter 8: constant_1 in Ksat EF
#parameter 9: constant_2 in Ksat EF
#parameter 10: sand_exp in Ksat EF

# do PSO calculations
#PSO parameters
w = 1 #intertia; weights the velocity at the previous step compared to velocity produced by local and global best positions
c1 = 0.7 #individual weight; weights the velocity change based off of individual particle's best position
c2 = 1.3 #global weight; weights the velocity chagne based off of global particles's best position
r1 = np.random.random()/2 + 0.75 #adds randomness to individual weight; between 0.75 and 1.25
r2 = np.random.random()/2 + 0.75 #adds randomness to social weight; between 0.75 and 1.25

#check if we need to initialize
#check_exists = exp_dir+'run/position_vals.csv'
if exists(os.path.join(exp_dir,'../','position_vals.csv')) == False:
    if from_restart == False:
        #positions = np.random.random((2,65))*2 #all random values between 0 and 2
        #velocities = np.random.random((2,65))
        positions = 0.25 + np.random.random((nparticles,nparameters))*3.75 #all random values between 0.25 and 4
        velocities = 0.5 - np.random.random((nparticles,nparameters))*1 #all random values between -0.5 and 0.5
        num_iterations = 0
        num_without_restart = 0
        iterations_without_change = 0
        best_positions = positions
        #best_positions_objective = np.zeros((2))
        best_positions_objective = np.zeros((nparticles))
        best_positions_objective[:] = float('inf')
        global_best_positions = np.zeros((nparameters))
        global_best_positions[:] = float('inf')
        global_best_objective = [float('inf')]

        iteration_track = pd.DataFrame({})
        iteration_track['iterations'] = [num_iterations]
        iteration_track['num_without_restart'] = [num_without_restart]
        iteration_track['iterations_without_change'] = [iterations_without_change]
        save_to = os.path.join(exp_dir,'run/iteration_track.csv')
    elif from_restart == True:
        iteration_track = pd.read_csv(
            os.path.join(
                pso_restart_dir,'iteration_track.csv'
            )
        )
        positions = np.genfromtxt(
            os.path.join(
                pso_restart_dir,'position_vals.csv'
            )
            ,delimiter=','
        )
        velocities = np.genfromtxt(
            os.path.join(
                pso_restart_dir,'velocity_vals.csv'
            )
            ,delimiter=','
        )
        best_positions = np.genfromtxt(
            os.path.join(
                pso_restart_dir,'best_positions.csv'
            )
            ,delimiter=','
        )
        best_positions_objective = np.genfromtxt(
            os.path.join(
                pso_restart_dir,'best_positions_objective.csv'
            )
            ,delimiter=','
        )
        global_best_positions = np.genfromtxt(
            os.path.join(
                pso_restart_dir,'global_best_positions.csv'
            )
            ,delimiter=','
        )
        global_best_objective = np.genfromtxt(
            os.path.join(
                pso_restart_dir,'global_best_objective.csv'
            )
            ,delimiter=','
        )
    
    # now save these
    iteration_track.to_csv(
        os.path.join(
            exp_dir,'../','iteration_track.csv'
        )
    )
    np.savetxt(
        os.path.join(
            exp_dir,'../','position_vals.csv'
        )
        ,positions,delimiter=','
    )
    np.savetxt(
        os.path.join(
            exp_dir,'../','velocity_vals.csv'
        )
        ,velocities,delimiter=','
    )
    np.savetxt(
        os.path.join(
            exp_dir,'../','best_positions.csv'
        )
        ,best_positions,delimiter=','
    )
    np.savetxt(
        os.path.join(
            exp_dir,'../','best_positions_objective.csv'
        )
        ,best_positions_objective,delimiter=','
    )
    np.savetxt(
        os.path.join(
            exp_dir,'../','global_best_positions.csv'
        )
        ,global_best_positions,delimiter=','
    )
    np.savetxt(
        os.path.join(
            exp_dir,'../','global_best_objective.csv'
        )
        ,global_best_objective,delimiter=','
    )


    #return convergence code to submit job
    if restart_every == 1:
        convergence = 2
    else:
        convergence = 1
    
    with open(o_file,'a') as f:
        f.write('finished with calcs for round 1')
        f.write('\n')
        f.write('convergence')
        f.write(str(convergence))
        f.write('\n')
        f.write('positions')
        f.write(str(positions))
        f.write('\n')
        f.write('velocities')
        f.write(str(velocities))
        f.write('\n')
    print(convergence)

else:
    #run as layed out previuosly
    iteration_track = pd.read_csv(
        os.path.join(
            exp_dir,'../','iteration_track.csv'
        )
    )
    num_iterations = iteration_track['iterations'].loc[0]
    num_without_restart = iteration_track['num_without_restart'].loc[0]
    iterations_without_change = iteration_track['iterations_without_change'].loc[0]


    if (num_iterations < spinup_iterations):
        #write to PSO_tracker.csv to keep track of variables
        num_iterations += 1
        num_without_restart += 1
        iterations_without_change = 0
        is_converged = 0
        # more will go here as I figure out what PSO values we will need in the next iteration....
    
        iteration_track['iterations'] = [num_iterations]
        iteration_track['num_without_restart'] = [num_without_restart]
        iteration_track['iterations_without_change'] = [iterations_without_change]
        iteration_track.to_csv(
            os.path.join(
                exp_dir,'../','iteration_track.csv'
            )
        )
    
        #copy the output files to a new location so that they can be analyzed if desired
        #for par in range(nparticles):
        for par in range(nparticles):
            src_path = os.path.join(exp_dir[:-2],str(par),'output/SMAP_EASEv2_M36/cat/ens0000/')
            dst_path = os.path.join('/discover/nobackup/projects/medComplex/pso_outputs',exp_dir[-5:-2],'num_'+str(num_iterations),str(par))
            if os.path.exists(dst_path) and os.path.isdir(dst_path):
                shutil.rmtree(dst_path)
            destination = shutil.copytree(src_path, dst_path)
    
    
        # determine value to return to lenkf.j
        if (is_converged == 1):
            convergence = 0
        elif (is_converged == 0 and (num_iterations <= max_iterations)
              and (num_without_restart < restart_every)):
            convergence = 1
        elif (is_converged == 0 and (num_iterations <= max_iterations)
              and (num_without_restart >= restart_every)):
            convergence = 2
            iteration_track['num_without_restart'] = 0
            iteration_track.to_csv(exp_dir+'/run/iteration_track.csv')
        elif (is_converged == 0 and (num_iterations > max_iterations)):
            convergence = 3
        with open(o_file,'a') as f:
            f.write(str('num_iterations'))
            f.write('\n')
            f.write(str(num_iterations))
            f.write('\n')
            f.write(str('iterations_without_change'))
            f.write('\n')
            f.write(str(iterations_without_change))
            f.write('\n')
    else:
        positions = np.genfromtxt(
            os.path.join(
                exp_dir,'../','position_vals.csv'
            )
            ,delimiter=','
        )
        velocities = np.genfromtxt(
            os.path.join(
                exp_dir,'../','velocity_vals.csv'
            )
            ,delimiter=','
        )
        best_positions = np.genfromtxt(
            os.path.join(
                exp_dir,'../','best_positions.csv'
            )
            ,delimiter=','
        )
        best_positions_objective = np.genfromtxt(
            os.path.join(
                exp_dir,'../','best_positions_objective.csv'
            )
            ,delimiter=','
        )
        global_best_positions = np.genfromtxt(
            os.path.join(
                exp_dir,'../','global_best_positions.csv'
            )
            ,delimiter=','
        )
        global_best_positions_last = np.copy(global_best_positions)
        global_best_objective = np.genfromtxt(
            os.path.join(
                exp_dir,'../','global_best_objective.csv'
            )
            ,delimiter=','
        )
        global_best_objective_last = np.copy(global_best_objective)
        
        #with open(o_file,'a') as f:
        #    f.write('loaded positions')
        #    f.write('\n')
        #    f.write(str(positions))
        #    f.write('\n')
    
        #objective function
        objective_result = compute_objective(
            exp_dir,nparticles,nparameters,positions
        ) #objective function to be filled in
    
    
        #best global position
        #update global best position
        objective_result_min_idx = np.argmin(objective_result)
        objective_result_min = objective_result[objective_result_min_idx]
        if objective_result_min < global_best_objective_last:
            global_best_positions = positions[objective_result_min_idx,:]
            global_best_objective = objective_result_min
            global_best_part = objective_result_min_idx
        
        local_improved_idx = np.where(objective_result < best_positions_objective)
        best_positions[local_improved_idx] = positions[local_improved_idx]
        best_positions_objective[local_improved_idx] = objective_result[local_improved_idx]
    
        #update velocity
        velocity_next = (w*velocities + c1*r2*(best_positions - positions) +
                         c2*r2*(np.tile(global_best_positions,(nparticles,1)) -
                                positions)
                        )
    
        #update positions
        positions_next = positions + velocity_next
    
        #save the updated arrays to their respective .csv files to be called in the next iteration
        global_best_objective = [global_best_objective]
        np.savetxt(
            os.path.join(
                exp_dir,'../','position_vals.csv'
            )
            ,positions_next,delimiter=','
        )
        np.savetxt(
            os.path.join(
                exp_dir,'../','velocity_vals.csv'
            )
            ,velocity_next,delimiter=','
        )
        np.savetxt(
            os.path.join(
                exp_dir,'../','best_positions.csv'
            )
            ,best_positions,delimiter=','
        )
        np.savetxt(
            os.path.join(
                exp_dir,'../','best_positions_objective.csv'
            )
            ,best_positions_objective,delimiter=','
        )
        np.savetxt(
            os.path.join(
                exp_dir,'../','global_best_positions.csv'
            )
            ,global_best_positions,delimiter=','
        )
        np.savetxt(
            os.path.join(
                exp_dir,'../','global_best_objective.csv'
            )
            ,global_best_objective,delimiter=','
        )
        #check if global best position vector has changed
        if np.all(global_best_positions_last == global_best_positions):
            iterations_without_change += 1
        else:
            iterations_without_change = 0
    
        #check if convergence has occured
        if iterations_without_change == convergence_threshold:
            is_converged = 1
        else:
            is_converged = 0
    
        #write to PSO_tracker.csv to keep track of variables
        num_iterations += 1
        num_without_restart += 1
        # more will go here as I figure out what PSO values we will need in the next iteration....
    
        iteration_track['iterations'] = [num_iterations]
        iteration_track['num_without_restart'] = [num_without_restart]
        iteration_track['iterations_without_change'] = [iterations_without_change]
        iteration_track.to_csv(
            os.path.join(
                exp_dir,'../','iteration_track.csv'
            )
        )
    
        #copy the output files to a new location so that they can be analyzed if desired
        #for par in range(nparticles):
        if iterations_without_change == 0:
            exp_name = os.path.split(os.path.split(exp_dir)[0])[1]
            src_path = os.path.join(exp_dir,'../',str(global_best_part),'output/SMAP_EASEv2_M36/cat/ens0000/')
            dst_path = os.path.join('/discover/nobackup/projects/medComplex/pso_outputs',
                                    exp_name,'num_'+str(num_iterations),str(global_best_part)
                                   )
            if os.path.exists(dst_path) and os.path.isdir(dst_path):
                shutil.rmtree(dst_path)
            destination = shutil.copytree(src_path, dst_path)
    
    
        # determine value to return to lenkf.j
        if (is_converged == 1):
            convergence = 0
        elif (is_converged == 0 and (num_iterations <= max_iterations)
              and (num_without_restart < restart_every)):
            convergence = 1
        elif (is_converged == 0 and (num_iterations <= max_iterations)
              and (num_without_restart >= restart_every)):
            convergence = 2
            iteration_track['num_without_restart'] = 0
            iteration_track.to_csv(exp_dir+'/run/iteration_track.csv')
        elif (is_converged == 0 and (num_iterations > max_iterations)):
            convergence = 3
        with open(o_file,'a') as f:
            f.write(str('num_iterations'))
            f.write('\n')
            f.write(str(num_iterations))
            f.write('\n')
            f.write(str('iterations_without_change'))
            f.write('\n')
            f.write(str(iterations_without_change))
            f.write('\n')
            f.write(str('velocities_last_iteration'))
            f.write('\n')
            f.write(str(velocities))
            f.write('\n')
            f.write(str('velocities_this_iteration'))
            f.write('\n')
            f.write(str(velocity_next))
            f.write('\n')
            f.write(str('positions_this_iteration'))
            f.write('\n')
            f.write(str(positions))
            f.write('\n')
            f.write(str('positions_next_iteration'))
            f.write('\n')
            f.write(str(positions_next))
            f.write('\n')
            f.write(str('objective_result'))
            f.write('\n')
            f.write(str(objective_result))
            f.write('\n')
            f.write(str('global_best_objective'))
            f.write('\n')
            f.write(str(global_best_objective))
            f.write('\n')
            f.write(str('global_best_positions'))
            f.write('\n')
            f.write(str(global_best_positions))
            f.write('\n')
            f.write(str('best_positions'))
            f.write('\n')
            f.write(str(best_positions))
            f.write('\n')
            f.write(str('best_positions_objective'))
            f.write('\n')
            f.write(str(best_positions_objective))
            f.write('\n')

    print(convergence)