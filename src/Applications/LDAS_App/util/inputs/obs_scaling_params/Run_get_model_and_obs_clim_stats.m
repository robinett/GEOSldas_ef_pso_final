% Calculate scaling files for Tb-DA based on SMAP Tb
%
% GDL, 11 Sep 2012
% QLiu, Dec 2016
%=====================================================================

clear

% add path to matlab functions in src/Applications/LDAS_App/util/shared/matlab/
addpath('../../shared/matlab/');

%======

run_months = [1:12 1:4]; %loop through 1:4 again to get complete pentads

% exp_path = '/discover/nobackup/amfox';
% exp_run  = {'SPL4SM_OL7000'};
% domain   = 'SMAP_EASEv2_M09_GLOBAL';

exp_path = '/discover/nobackup/amfox/Experiments/ASCAT_3Y_v2';
exp_run  = {'ASCAT_M36'};
domain   = 'SMAP_EASEv2_M36_GLOBAL';

%Start and end year for each month
start_year = [repmat(2016,1,5) repmat(2015,1,7) repmat(2016,1,4)]; %corresp to [1:12 1 2]
end_year   = [repmat(2017,1,5) repmat(2016,1,7) repmat(2017,1,4)]; %runs till end of run_months for end_year


%d orbit    = [ 2]; %1=A, 2=D   !DO *NOT* USE ASC AND DESC TOGETHER!
%d pol      = [ 1 2 ]; %1=H, 2=V
%d inc_ang  = [ 40.0 ];

prefix_out = 'L4SM_OL7000_SMAPL1CR17000_zscore_stats_';
prefix_out = 'M36_zscore_stats_';

dt_assim   = 3*60*60;    % [seconds] land analysis time step,
                         %             same as LANDASSIM_DT in GEOSldas)
t0_assim   =       0;    % [seconds] land analysis "reference" time (offset from 0z), 
                         %             same as LANDASSIM_T0 in GEOSldas (except for units),  
                         %             typically 0 in offline runs and 1.5*60*60 in LADAS

%======

obs_param_fname = [exp_path, '/', exp_run{1}, '/output/', domain, '/rc_out/', ...
    '/Y2016/M04/',exp_run{1}, '.ldas_obsparam.20160401_0000z.txt'];

%d var_name = {'Tb'};

% added to identify SMOS or SMAP from runs that include both
species_names = {'SMAP_L1C_Tbh_A', 'SMAP_L1C_Tbv_A', 'SMAP_L1C_Tbh_D', 'SMAP_L1C_Tbv_D'};
species_names = {'ASCAT_META_SM_A','ASCAT_META_SM_D','ASCAT_METB_SM_A','ASCAT_METB_SM_D'};
species_names = {'ASCAT_META_SM_A','ASCAT_META_SM_D'};

%======
%d if (length(orbit) > 1)
 %d    error('ONLY pick one orbit!'
%d end

%d if (orbit(1) == 1) int_Asc = 1; end %Asc
%d if (orbit(1) == 2) int_Asc = 0; end %Desc

%======
%TO GO FROM SMOS TO SMAP ONLY!!!
%int_Asc = abs(int_Asc - 1);
%======

%Spatial sampling
hscale = 0.0;          % degrees lat/lon

% Temporal sampling window(days), current hard coded and need to be divisive by 5 and be an odd number
w_days    = 75;  

Ndata_min = 20;

%To limit M09 tiles to administering M36 tiles only (smaller files),
%provide convert_grid
if isempty(strfind(prefix_out,'M09'))
    convert_grid='EASEv2_M36';
end

if (mod(w_days,10) == 0)
    disp('w_days should be 5, 15, 25, 35, ...')
    error('Need an odd number of pentads |xxxxx|xxXxx|xxxxx|')
end
if (mod(w_days, 5) > 0)
    error('Aiming at pentad files')
end

% ------------------------------------------------------------------------

[N_obs_param, obs_param ] = read_obsparam(obs_param_fname);

species =[];

% for oo=1:length(orbit)
%     for pp=1:length(pol)
%         for aa=1:length(inc_ang)
%                         
%             add_species = obs_param(strcmp(var_name,{obs_param.varname}) & ...
%                 orbit(oo) == [obs_param.orbit] & ...
%                 inc_ang(aa) == [obs_param.ang] & ...
%                 pol(pp) == [obs_param.pol] & ...
%                 ~cellfun(@isempty, strfind({obs_param.descr},descr))).species;
%                                      
%             species = union(species,add_species);
%             
%         end
%     end
% end

for i = 1:length(species_names)
    add_species = obs_param(strcmp(species_names(i),{obs_param.descr})).species;
    species = union(species,add_species);
end

species
% ------------------

for n=1:length(exp_run)
    
    if (exist('convert_grid','var'))
        
        if exist('time_of_day_in_hours','var')
            
            
            for j=1:length(time_of_day_in_hours)
                
                for k=1:length(run_months)
                    
                    get_model_and_obs_clim_stats( species_names,               ...
                        run_months{k}, exp_path, exp_run{n}, domain,     ...
                        start_year, end_year, ...
                        dt_assim, t0_assim, species, obs_param, ...
                        hscale, w_days, Ndata_min, prefix_out,...
                        convert_grid, time_of_day_in_hours(j)  );
                    
                end
                
            end
            
        else
            
            get_model_and_obs_clim_stats( species_names,                              ...
                run_months, exp_path, exp_run{n}, domain, start_year, end_year, ...
                dt_assim, t0_assim, species, obs_param, ...
                hscale, w_days, Ndata_min, prefix_out,...
                convert_grid );
            
        end
    else
        
        if exist('time_of_day_in_hours','var')
            
            
            for j=1:length(time_of_day_in_hours)
                
                for k=1:length(run_months)
                    
                    get_model_and_obs_clim_stats( species_names,               ...
                        run_months{k}, exp_path, exp_run{n}, domain,     ...
                        start_year, end_year, ...
                        dt_assim, t0_assim, species, obs_param, ...
                        hscale, w_days, Ndata_min, prefix_out,...
                        time_of_day_in_hours(j)  );
                    
                end
                
            end
            
        else
            
            get_model_and_obs_clim_stats( species_names,                              ...
                run_months, exp_path, exp_run{n}, domain, start_year, end_year, ...
                dt_assim, t0_assim, species, obs_param, ...
                hscale, w_days, Ndata_min, prefix_out);
            
        end
        
    end
end


% ============= EOF ====================================================

