from collections import Counter

# goal consists of (item, remaining time)
goals = [('cooked_chicken', 12)]
chest = {'cooked_chicken': 1}
accomplished_goals = []

# Sort the goals based on time
goals.sort(key=lambda x: x[1])

remaining_goals = goals.copy()  # Create a copy to iterate over

for goal in remaining_goals:
    item, _ = goal
    if item in chest:
        accomplished_counter = Counter(accomplished_goals)
        if accomplished_counter[item] < chest[item]:
            accomplished_goals.append(item)
            goals.remove(goal)

print(accomplished_goals)