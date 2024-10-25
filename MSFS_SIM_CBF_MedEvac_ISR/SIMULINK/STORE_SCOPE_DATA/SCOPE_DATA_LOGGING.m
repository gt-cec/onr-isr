%%%%%%%%%%%%%%%%%%%%%%%%%%%%% SCOPE LOGGING FILE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Carmen Thiemann
% 10/23/2024
% Description: File to log data from scope after sim run
%% IMPORT DATA %%
% In Scope to export select: options > logging > log data to workspace >
% STRUCTURE WITH TIME (update name both in scope block and in this code)
time_stamps = out.ALPHA_VALUE.time;
scope_value = squeeze(out.ALPHA_VALUE.signals.values);
%% COMBINE DATA AND EXPORT
combinedScopeData = [time_stamps, scope_value];
writematrix(combinedScopeData, '400_A4_Alpha.csv');
% plot(time_stamps,scope_value)
