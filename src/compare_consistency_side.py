import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import beta

NUM_CLIPS = 0

def calculate_angle(vertex, a, b):
    """
    Calculate angle (in degrees) for (a -> vertex -> b)

    Inputs:
        a       = point 1 (e.g., shoulder)
        vertex  = point 2 (e.g., elbow)
        b       = point 3 (e.g., wrist)

    Output:
        Angle in degrees between a -> vertex -> b.
    """
    AV = (a[0] - vertex[0], a[1] - vertex[1])
    BV = (b[0] - vertex[0], b[1] - vertex[1])
    
    dot_product = AV[0] * BV[0] + AV[1] * BV[1]
    AV_magnitude = math.sqrt(AV[0]**2 + AV[1]**2)
    BV_magnitude = math.sqrt(BV[0]**2 + BV[1]**2)
    
    if AV_magnitude == 0 or BV_magnitude == 0:
        return 0.0
    
    cos_value = max(min(dot_product / (AV_magnitude * BV_magnitude), 1.0), -1.0)
    return math.degrees(math.acos(cos_value))

def generate_side_la_parameters(data):
    sew_la_list = []
    ewa_la_list = []

    for i in range(len(data["ball"])):
        # shoulder-elbow-wrist left arm
        if ((data["left_shoulder"][i] != None) and (data["left_elbow"][i] != None) and (data["left_wrist"][i] != None)):
            angle = calculate_angle(data["left_elbow"][i], data["left_shoulder"][i], data["left_wrist"][i])
            sew_la_list.append(angle)
        
        # elbow-wrist-average left arm (avg = thumb and pinky)
        if ((data["left_elbow"][i] != None) and (data["left_wrist"][i] != None)):
            if (data["left_pinky"][i] != None and data["left_thumb"][i] != None):
                x = (data["left_pinky"][i][0] + data["left_thumb"][i][0]) / 2
                y = (data["left_pinky"][i][1] + data["left_thumb"][i][1]) / 2
                coord = [x, y]
                angle = calculate_angle(data["left_wrist"][i], data["left_elbow"][i], coord)
                ewa_la_list.append(angle)
    
    sew_la = get_parameters(sew_la_list)
    ewa_la = get_parameters(ewa_la_list)

    return sew_la, ewa_la

def generate_side_ra_parameters(data):
    sew_ra_list = []
    ewp_ra_list = []
    hse_ra_list = []
    
    for i in range(len(data["ball"])):
        # shoulder-elbow-wrist right arm
        if ((data["right_shoulder"][i] != None) and (data["right_elbow"][i] != None) and (data["right_wrist"][i] != None)):
            angle = calculate_angle(data["right_elbow"][i], data["right_shoulder"][i], data["right_wrist"][i])
            sew_ra_list.append(angle)
        
        # elbow-wrist-pinky right arm
        if ((data["right_elbow"][i] != None) and (data["right_wrist"][i] != None) and (data["right_pinky"][i] != None)):
            angle = calculate_angle(data["right_wrist"][i], data["right_elbow"][i], data["right_pinky"][i])
            ewp_ra_list.append(angle)

        # hip-shoulder-elbow right arm     
        if ((data["right_hip"][i] != None) and (data["right_shoulder"][i] != None) and (data["right_elbow"][i] != None)):
            angle = calculate_angle(data["right_shoulder"][i], data["right_hip"][i], data["right_elbow"][i])
            hse_ra_list.append(angle)  
    
    sew_ra = get_parameters(sew_ra_list)
    ewp_ra = get_parameters(ewp_ra_list)
    hse_ra = get_parameters(hse_ra_list)

    return sew_ra, ewp_ra, hse_ra

def get_parameters(angles, max_val=180):
    """
    Calculates distribution parameters for a given set of angles by scaling
    them to the [0,1] interval and fitting a Beta distribution.
    
    Inputs:
        angles  = numpy array of angles (in degrees)
        max_val = maximum angle value (default is 180)
    
    Outputs:
        A dictionary containing:
            - mean: sample mean (in degrees)
            - std: sample standard deviation (in degrees)
            - alpha: Beta distribution alpha parameter
            - beta: Beta distribution beta parameter
    """
    angles = np.array(angles)
    mean_val = float(np.mean(angles))
    std_val = float(np.std(angles))
    cv = (std_val / mean_val) * 100     # coefficient of variation normalizes consistency regardless of magnitude
    
    return cv

def generate_plot(dist_params_sew, dist_params_ewa, arm_name, save_plot=True):
    """
    Generates and (optionally) displays/saves a plot of the weighted bell curves
    for the given distribution parameters using a Beta distribution scaled to [0,180].
    
    Inputs:
        dist_params_sew  = distribution parameters for shoulder-elbow-wrist angles
        dist_params_ewa  = distribution parameters for elbow-wrist-average angles
        arm_name         = string indicating the arm ("left" or "right")
        save_plot        = if True, the plot is saved to file
    """
    x = np.linspace(0, 180, 200)
    
    alpha_sew = dist_params_sew["alpha"]
    beta_sew = dist_params_sew["beta"]
    alpha_ewa = dist_params_ewa["alpha"]
    beta_ewa = dist_params_ewa["beta"]
    
    # Compute the Beta PDFs transformed to the [0,180] domain.
    y_sew = (1/180.0) * beta.pdf(x/180.0, alpha_sew, beta_sew)
    y_ewa = (1/180.0) * beta.pdf(x/180.0, alpha_ewa, beta_ewa)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y_sew, label='Shoulder-Elbow-Wrist Angles', color='blue')
    plt.plot(x, y_ewa, label='Elbow-Wrist-Average(Pinky, Index) Angles', color='red')
    plt.title(f'Weighted Bell Curves for {arm_name.capitalize()} Arm Angles\n(Beta Distribution)')
    plt.xlabel('Angle (Degrees)')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    
    if save_plot:
        plot_filename = f"{arm_name}_arm_bell_curve.png"
        plt.savefig(plot_filename)
        print(f"Saved {arm_name} arm bell curve plot to '{plot_filename}'")
    plt.close()


def prep_data(dict_list):
    merged_dict = {
        'left_shoulder': [], 'right_shoulder': [], 'left_elbow': [], 'right_elbow': [],
        'left_wrist': [], 'right_wrist': [], 'left_hip': [], 'right_hip': [],
        'left_pinky': [], 'right_pinky': [], 'left_thumb': [], 'right_thumb': [],
        'ball': []
    }
    
    for d in dict_list:
        for key in merged_dict:
            merged_dict[key].append(d.get(key, None))
    
    return merged_dict

def get_consistency_side(dict_list):
    data = prep_data(dict_list)
    sew_ra, ewp_ra, hse_ra = generate_side_ra_parameters(data)

    weights = (sew_ra, ewp_ra, hse_ra) / 3
    return weights


def main():
    return 0

if __name__ == "__main__":
    main()
