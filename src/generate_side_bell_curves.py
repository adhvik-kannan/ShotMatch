import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import beta
import ast
import re

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
    print(f"angles: {angles}")
    angles = np.array(angles)
    if len(angles) == 0:
        return {"mean": 0.0, "std": 0.0, "alpha": 100, "beta": 100}
    mean_val = float(np.mean(angles))
    std_val = float(np.std(angles))
    m_y = mean_val / max_val
    s_y_sq = (std_val**2) / (max_val**2)
    
    if s_y_sq <= 0:
        alpha = beta_val = 100  # default, very peaked
    else:
        factor = (m_y * (1 - m_y) / s_y_sq) - 1
        alpha = m_y * factor
        beta_val = (1 - m_y) * factor
    
    return {"mean": mean_val, "std": std_val, "alpha": alpha, "beta": beta_val}

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


def plot_beta_distribution(params, title):
    # print(f"params: {params}")
    alpha = params["alpha"]
    beta_val = params["beta"]
    
    x = np.linspace(0, 1, 100)          # Generate x values between 0 and 1=
    y = beta.pdf(x, alpha, beta_val)    # Compute the Beta probability density function (PDF)

    # plot
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, label=f'Beta({alpha:.2f}, {beta_val:.2f})', color='b')
    plt.fill_between(x, y, alpha=0.3, color='blue')  
    plt.xlabel('x')
    plt.ylabel('Density')
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()


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


def parse_data(file_content):
    waist_data = []
    eye_data = []
    hand_data = []
    
    entries = file_content.strip().split('\n')
    
    for entry in entries:
        if not entry.strip() or entry.strip().lower() == 'none':
            continue
            
        try:
            # Extract player ID and position, only for klay_side_ra_ entries
            match = re.match(r'(klay_side_ra_\d+)\s+(\w+):\s+(.+)', entry)
            if not match:
                # Skip entries that don't match the side pattern
                continue
                
            player_id, position, data_str = match.groups()
            
            # Skip if data_str is 'None'
            if data_str.strip().lower() == 'none':
                continue
                
            # Parse the dictionary string
            try:
                data_dict = ast.literal_eval(data_str)
            except (SyntaxError, ValueError) as e:
                print(f"Error parsing dictionary in entry: {entry[:50]}... Error: {e}")
                continue
            
            # Ensure data_dict is a dictionary
            if not isinstance(data_dict, dict):
                print(f"Skipping entry, data_dict is not a dictionary: {entry[:50]}...")
                continue
                
            # Add player_id to the dictionary
            data_dict['player_id'] = player_id
            
            # Categorize based on position
            if position.lower() == 'waist':
                waist_data.append(data_dict)
            elif position.lower() == 'eye':
                eye_data.append(data_dict)
            elif position.lower() == 'max_hand':
                hand_data.append(data_dict)
            else:
                print(f"Unknown position '{position}' in entry: {entry[:50]}...")
                    
        except Exception as e:
            print(f"Error processing entry: {entry[:50]}... Error: {e}")
            continue
    
    return waist_data, eye_data, hand_data

def main():
    # parse data from data_klay.txt
    with open('data_klay.txt', 'r') as file:
        file_content = file.read()
    
    waist_data, eye_data, max_data = parse_data(file_content)
        
    waist_data = prep_data(waist_data)
    eye_data = prep_data(eye_data)
    max_data = prep_data(max_data)

    print("Waist Data:", len(waist_data['left_shoulder']), "entries")
    print("Eye Data:", len(eye_data['left_shoulder']), "entries")
    print("Max Hand Data:", len(max_data['left_shoulder']), "entries")

    data = max_data
    name = "MAX"

    # generate parameters
    s_sew_ra, s_ewp_ra, s_hse_ra = generate_side_ra_parameters(data)
    # s_sew_la, s_ewa_la = generate_side_la_parameters(data)

    # right arm
    print(f"{name}_S_EWP_RA: {s_ewp_ra}")
    print(f"{name}_S_HSE_RA: {s_hse_ra}")
    print(f"{name}_S_SEW_RA: {s_sew_ra}")

    plot_beta_distribution(s_ewp_ra, name + "_S_EWP_RA")
    plot_beta_distribution(s_hse_ra, name + "_S_HSE_RA")
    plot_beta_distribution(s_sew_ra, name + "_S_SEW_RA")
    

    # left arm
    # print(f"{name}_S_EWA_LA: {s_ewa_la}")
    # print(f"{name}_S_SEW_LA: {s_sew_la}")
    # plot_beta_distribution(s_ewa_la, name + "_F_EWA_LA")
    # plot_beta_distribution(s_sew_la, name + "_F_SEW_LA")
    

if __name__ == "__main__":
    main()
