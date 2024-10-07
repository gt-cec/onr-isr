%% GENERATE SATELLITE VIEW OF TRAJECTORY
% Generate data from simulation
lat_data = squeeze(out.LAT_DATA.signals.values);
lat_data_deg = lat_data*180/pi;
lat_data_deg = lat_data_deg(106:end); % Remove bus init value
long_data = squeeze(out.LONG_DATA.signals.values);
long_data_deg = long_data*180/pi;
long_data_deg = long_data_deg(106:end); % Remove bus init value

webmap('World Imagery') % Opens world map satellite view
trajectory = geoshape(lat_data_deg, long_data_deg); % Creates the trajectory from simulation data in degrees
wmline(trajectory, 'Color', 'red', 'Width', 3) % Plots the line on top of the map