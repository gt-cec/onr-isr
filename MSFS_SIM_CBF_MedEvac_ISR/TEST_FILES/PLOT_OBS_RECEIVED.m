OBS_LAT_ARRAY = out.OBS_LAT.signals.values;
OBS_LAT_ARRAY_WP = OBS_LAT_ARRAY(:,1,end);
OBS_LONG_ARRAY = out.OBS_LONG.signals.values;
OBS_LONG_ARRAY_WP = OBS_LONG_ARRAY(:,1,end);
geolimits([32.28 33.72],[-118.72 -117.28])
% geoplot(OBS_LAT_ARRAY_WP(1), OBS_LONG_ARRAY_WP(1),'*')
%hold on
for i=1:1:length(OBS_LONG_ARRAY_WP)
geoplot(OBS_LAT_ARRAY_WP(i), OBS_LONG_ARRAY_WP(i),'*')
hold on
end