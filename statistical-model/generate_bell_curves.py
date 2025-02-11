import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import norm
import json

NUM_CLIPS = 0

def calculate_angle(vertex, a, b):
    """
    calculate angle (degrees) for (a -> vertex -> b)

    """
    AV = (a[0] - vertex[0], a[1] - vertex[1])
    BV = (b[0] - vertex[0], b[1] - vertex[1])
    
    dot_product = AV[0]*BV[0] + AV[1]*BV[1]
    AV_magnitude = math.sqrt(AV[0]**2 + AV[1]**2)
    BV_magnitude = math.sqrt(BV[0]**2 + BV[1]**2)
    
    if AV_magnitude == 0 or BV_magnitude == 0:
        return 0.0
    
    cos_value = max(min(dot_product / (AV_magnitude * BV_magnitude), 1.0), -1.0)
    return math.degrees(math.acos(cos_value))

def process_arm_data(shoulder, elbow, wrist, pinky, index):
    """
    makes 2 arrays
    ewa: elbow -> wrist -> avg(index/pinky)
    sew: shoulder -> elbow -> wrist

    """
    angle_sew_list = []  
    angle_ewa_list = []  
    
    for i in range(len(shoulder)):  # can also be range(NUM_CLIPS) i think but its safer this way
        s = shoulder[i]
        e = elbow[i]
        w = wrist[i]
        p = pinky[i]
        idx = index[i]
        
        # angles
        angle_sew = calculate_angle(e, s, w)
        angle_sew_list.append(angle_sew)

        avg_pinky_index = [(p[0] + idx[0]) / 2, (p[1] + idx[1]) / 2]
        angle_ewa = calculate_angle(w, e, avg_pinky_index)
        angle_ewa_list.append(angle_ewa)

        # print(f"ANGLE SEW: {angle_sew}, ANGLE EWA: {angle_ewa}")
    
    return np.array(angle_sew_list), np.array(angle_ewa_list)



# ------------------------------------------------------------------------------------------------
# this is from gpt lol
# ------------------------------------------------------------------------------------------------
def plot_and_save(angles_sew, angles_ewa, arm_name):
    """
    Plots the two bell curves (one for each angle distribution), saves the plot, and saves
    the distribution parameters in a JSON file.
    
    """
    # Compute mean and std for each angle distribution.
    mean_sew = float(np.mean(angles_sew))
    std_sew = float(np.std(angles_sew))
    
    mean_ewa = float(np.mean(angles_ewa))
    std_ewa = float(np.std(angles_ewa))
    
    # Generate bell curve data for the shoulder-elbow-wrist angles.
    x_sew = np.linspace(mean_sew - 4 * std_sew, mean_sew + 4 * std_sew, 100)
    y_sew = norm.pdf(x_sew, mean_sew, std_sew)
    
    # Generate bell curve data for the elbow-wrist-average angles.
    x_ewa = np.linspace(mean_ewa - 4 * std_ewa, mean_ewa + 4 * std_ewa, 100)
    y_ewa = norm.pdf(x_ewa, mean_ewa, std_ewa)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x_sew, y_sew, label='Shoulder-Elbow-Wrist Angles', color='blue')
    plt.plot(x_ewa, y_ewa, label='Elbow-Wrist-Average(Pinky,Index) Angles', color='red')
    plt.title(f'Weighted Bell Curves for {arm_name.capitalize()} Arm Angles')
    plt.xlabel('Angle (Degrees)')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.grid(True)
    
    # Save the plot image.
    plot_filename = f"{arm_name}_arm_bell_curve.png"
    plt.savefig(plot_filename)
    plt.close()
    
    # Save the distribution parameters to a JSON file.
    distribution_params = {
        "shoulder_elbow_wrist": {"mean": mean_sew, "std": std_sew},
        "elbow_wrist_avg_pinky_index": {"mean": mean_ewa, "std": std_ewa}
    }
    json_filename = f"{arm_name}_arm_angle_distribution.json"
    with open(json_filename, "w") as f:
        json.dump(distribution_params, f, indent=4)
    
    print(f"Saved {arm_name} arm bell curve plot to '{plot_filename}'")
    print(f"Saved {arm_name} arm distribution parameters to '{json_filename}'")



def main():
    # get data from left arm json file 
    try:
        with open("left_arm_data.json", "r") as f_left:
            left_data = json.load(f_left)
    except FileNotFoundError:
        print("Error: 'left_arm_data.json' not found. Please provide the left arm data.")
        return
    
    # get data from right arm json file
    try:
        with open("right_arm_data.json", "r") as f_right:
            right_data = json.load(f_right)
    except FileNotFoundError:
        print("Error: 'right_arm_data.json' not found. Please provide the right arm data.")
        return
    
    # puill from json file
    left_shoulder = left_data["shoulder"]
    left_elbow = left_data["elbow"]
    left_wrist = left_data["wrist"]
    left_pinky = left_data["pinky"]
    left_index = left_data["index"]
    
    right_shoulder = right_data["shoulder"]
    right_elbow = right_data["elbow"]
    right_wrist = right_data["wrist"]
    right_pinky = right_data["pinky"]
    right_index = right_data["index"]

    # gen agnles
    left_angle_sew, left_angle_ewa = process_arm_data(left_shoulder, left_elbow, left_wrist, left_pinky, left_index)
    right_angle_sew, right_angle_ewa = process_arm_data(right_shoulder, right_elbow, right_wrist, right_pinky, right_index)
    
    # gen plots and save to file
    plot_and_save(left_angle_sew, left_angle_ewa, "left")
    plot_and_save(right_angle_sew, right_angle_ewa, "right")

if __name__ == "__main__":
    main()


# SAMPLE JSON FORMAT
# {
#   "shoulder": [
#     [x, y],
#     [x, y]
#   ],
#   "elbow": [
#     [x, y],
#     [x, y]
#   ],
#   "wrist": [
#     [x, y],
#     [x, y]
#   ],
#   "pinky": [
#     [x, y],
#     [x, y]
#   ],
#   "index": [
#     [x, y],
#     [x, y]
#   ]
# }