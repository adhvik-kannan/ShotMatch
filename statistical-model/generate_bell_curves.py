import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import beta
import json

NUM_CLIPS = 0

def calculate_angle(vertex, a, b):
    """
    calculate angle (in degrees) for (a -> vertex -> b)

    Inputs:
        a       = point 1
        vertex  = point 2
        b       = point 3

    Outputs:
        degrees = degrees between a -> vertex -> b
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
    Processes frames of data for one arm and computes two arrays:
      - sew: Shoulder -> Elbow -> Wrist angles (computed at the elbow)
      - ewa: Elbow -> Wrist -> Average(Pinky, Index) angles (computed at the wrist)
    
    Inputs: 
        shoulder    = shoulder coordinate 
        elbow       = elbow coordinate
        wrist       = wrist coordinate
        pinky       = pinky coordinate
        index       = index coordinate
    
    Outputs:
        angle_sew_list  = list of angles for each dataframe in input-file for shoulder->elbow->wrist
        angle_ewa_list  = list of angles for each dataframe in input-file for elbow->wrist->fingers
    """
    angle_sew_list = []  
    angle_ewa_list = []  
    
    for i in range(len(shoulder)):
        s = shoulder[i]
        e = elbow[i]
        w = wrist[i]
        p = pinky[i]
        idx = index[i]
        
        angle_sew = calculate_angle(e, s, w)
        angle_sew_list.append(angle_sew)
        
        avg_pinky_index = [(p[0] + idx[0]) / 2, (p[1] + idx[1]) / 2]
        angle_ewa = calculate_angle(w, e, avg_pinky_index)
        angle_ewa_list.append(angle_ewa)
    
    return np.array(angle_sew_list), np.array(angle_ewa_list)

def plot_and_save(angles_sew, angles_ewa, arm_name):
    """
    generates weighted bell curves for given angle distributions using a beta distribution
    scaled to [0, 180] degrees. curve is centered around the mean of the data.
    
    Inputs:
        angles_sew  = shoulder elbow wrist angle list
        angles_ewa  = elbow wrist fingers angle list
        arm_name    = either left or right arm
    """
    mean_sew = float(np.mean(angles_sew))
    std_sew = float(np.std(angles_sew))
    
    mean_ewa = float(np.mean(angles_ewa))
    std_ewa = float(np.std(angles_ewa))
    
    m_y_sew = mean_sew / 180.0
    s_y_sew_sq = (std_sew**2) / (180.0**2)
    
    m_y_ewa = mean_ewa / 180.0
    s_y_ewa_sq = (std_ewa**2) / (180.0**2)
    
    # beta distribution for the sew angles
    if s_y_sew_sq <= 0:
        alpha_sew = beta_sew = 100  # peaked default
    else:
        factor_sew = (m_y_sew*(1 - m_y_sew) / s_y_sew_sq) - 1
        alpha_sew = m_y_sew * factor_sew
        beta_sew = (1 - m_y_sew) * factor_sew
    
    # beta distribution for the ewa angles
    if s_y_ewa_sq <= 0:
        alpha_ewa = beta_ewa = 100  # peaked defualt
    else:
        factor_ewa = (m_y_ewa*(1 - m_y_ewa) / s_y_ewa_sq) - 1
        alpha_ewa = m_y_ewa * factor_ewa
        beta_ewa = (1 - m_y_ewa) * factor_ewa
    

    x = np.linspace(0, 180, 200)

    # beta PDF f_x(x) = (1/180)*f_y(x/180) and transform
    y_sew = (1/180.0) * beta.pdf(x/180.0, alpha_sew, beta_sew)
    y_ewa = (1/180.0) * beta.pdf(x/180.0, alpha_ewa, beta_ewa)
    

    # plots
    plt.figure(figsize=(10, 6))
    plt.plot(x, y_sew, label='Shoulder-Elbow-Wrist Angles', color='blue')
    plt.plot(x, y_ewa, label='Elbow-Wrist-Average(Pinky, Index) Angles', color='red')
    plt.title(f'Weighted Bell Curves for {arm_name.capitalize()} Arm Angles\n(Beta Distribution)')
    plt.xlabel('Angle (Degrees)')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    
    plot_filename = f"{arm_name}_arm_bell_curve.png"
    plt.savefig(plot_filename)
    plt.close()
    
    # save params to a JSON 
    distribution_params = {
        "shoulder_elbow_wrist": {
            "mean": mean_sew,
            "std": std_sew,
            "alpha": alpha_sew,
            "beta": beta_sew
        },
        "elbow_wrist_avg_pinky_index": {
            "mean": mean_ewa,
            "std": std_ewa,
            "alpha": alpha_ewa,
            "beta": beta_ewa
        }
    }
    json_filename = f"{arm_name}_arm_angle_distribution.json"
    with open(json_filename, "w") as f:
        json.dump(distribution_params, f, indent=4)
    
    print(f"Saved {arm_name} arm bell curve plot to '{plot_filename}'")
    print(f"Saved {arm_name} arm distribution parameters to '{json_filename}'")

def main():
    # Read left arm data from a JSON file.
    try:
        with open("left_arm_data.json", "r") as f_left:
            left_data = json.load(f_left)
    except FileNotFoundError:
        print("Error: 'left_arm_data.json' not found. Please provide the left arm data.")
        return
    
    # Read right arm data from a JSON file.
    try:
        with open("right_arm_data.json", "r") as f_right:
            right_data = json.load(f_right)
    except FileNotFoundError:
        print("Error: 'right_arm_data.json' not found. Please provide the right arm data.")
        return
    
    # Pull data from the JSON files.
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

    # Generate angles for each arm.
    left_angle_sew, left_angle_ewa = process_arm_data(left_shoulder, left_elbow, left_wrist, left_pinky, left_index)
    right_angle_sew, right_angle_ewa = process_arm_data(right_shoulder, right_elbow, right_wrist, right_pinky, right_index)
    
    # Generate plots and save distribution parameters for each arm.
    plot_and_save(left_angle_sew, left_angle_ewa, "left")
    plot_and_save(right_angle_sew, right_angle_ewa, "right")

if __name__ == "__main__":
    main()
