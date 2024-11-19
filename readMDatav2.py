import pickle
#file_name = input("Enter file name: ")
with open('None_none.pkl', 'rb') as file:
    allMouseData = pickle.load(file)
    phaseData = pickle.load(file)
    clickData = pickle.load(file)
    alertData = pickle.load(file)
    targetData = pickle.load(file)
    for coord in allMouseData:
        print(f"{coord}")
    for phase in phaseData:
        print(f"{phase}")
    for click in clickData:
        print(f"{click}")
    for alert in alertData:
        print(f"{alert}")
    for target in targetData:
        print(f"{target}")