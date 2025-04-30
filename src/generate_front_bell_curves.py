import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import beta
import ast
import re

NUM_CLIPS = 0

def calculate_acute_angle(vertex, a, b):
    """
    Calculate the angle (in degrees) between three points: a -> vertex -> b.
    
    Inputs:
        a       = point 1 (e.g., hip for hew, shoulder for sew, or elbow for ewp)
        vertex  = point 2 (e.g., shoulder for hew, elbow for sew, or wrist for ewp)
        b       = point 3 (e.g., elbow for hew, wrist for sew, or pinky for ewp)
    
    Output:
        Angle in degrees between a -> vertex -> b.
    """
    AV = (abs(a[0] - vertex[0]), abs(a[1] - vertex[1]))
    BV = (abs(b[0] - vertex[0]), abs(b[1] - vertex[1]))
    
    dot_product = AV[0]*BV[0] + AV[1]*BV[1]
    AV_magnitude = math.sqrt(AV[0]**2 + AV[1]**2)
    BV_magnitude = math.sqrt(BV[0]**2 + BV[1]**2)
    
    if AV_magnitude == 0 or BV_magnitude == 0:
        return 0.0
    
    cos_value = max(min(dot_product / (AV_magnitude * BV_magnitude), 1.0), -1.0)
    return math.degrees(math.acos(cos_value))

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

def generate_front_parameters(data):
    """
    Processes frames of front-view data and computes four arrays:
      - hew: Hip -> Shoulder -> Elbow angles (vertex = shoulder)
      - sew: Shoulder -> Elbow -> Wrist angles (vertex = elbow)
      - ewp: Elbow -> Wrist -> Pinky angles (vertex = wrist)
      - ec : Elbow Comparison metric = (|left_elbow_y - right_elbow_y|) / (distance between left_wrist and left_elbow)
    
    Inputs:
        hip         = list of hip coordinates
        shoulder    = list of shoulder coordinates
        left_elbow  = list of left elbow coordinates
        right_elbow = list of right elbow coordinates
        wrist       = list of wrist coordinates
        pinky       = list of pinky coordinates
        
    Outputs:
        hew_array, sew_array, ewp_array, ec_array as numpy arrays.
    """
    hew_ra_list = []
    hew_la_list = []
    sew_ra_list = []
    sew_la_list = []
    ewa_ra_list = []
    ewp_la_list = []
    
    for i in range(len(data["ball"])):
        # hip-elbow-wrist right arm
        if ((data["right_hip"][i] != None) and (data["right_wrist"][i] != None) and (data["right_elbow"][i] != None)):
            angle = calculate_angle(data["right_elbow"][i], data["right_hip"][i], data["right_wrist"][i])
            hew_ra_list.append(angle)
        
        # hip-elbow-wrist left arm
        if ((data["left_hip"][i] != None) and (data["left_wrist"][i] != None) and (data["left_elbow"][i] != None)):
            angle = calculate_angle(data["left_elbow"][i], data["left_hip"][i], data["left_wrist"][i])
            hew_la_list.append(angle)

        # shoulder-elbow-wrist right arm
        if ((data["right_shoulder"][i] != None) and (data["right_elbow"][i] != None) and (data["right_wrist"][i] != None)):
            angle = calculate_acute_angle(data["right_elbow"][i], data["right_shoulder"][i], data["right_wrist"][i])
            sew_ra_list.append(angle)
        
        # shoulder-elbow-wrist left arm
        if ((data["left_shoulder"][i] != None) and (data["left_elbow"][i] != None) and (data["left_wrist"][i] != None)):
            angle = calculate_acute_angle(data["left_elbow"][i], data["left_shoulder"][i], data["left_wrist"][i])
            sew_la_list.append(angle)
        
        # elbow-wrist-average right arm (avg = thumb and pinky)
        if ((data["right_elbow"][i] != None) and (data["right_wrist"][i] != None)):
            if (data["right_pinky"][i] != None and data["right_thumb"][i] != None):
                x = (data["right_pinky"][i][0] + data["right_thumb"][i][0]) / 2
                y = (data["right_pinky"][i][1] + data["right_thumb"][i][1]) / 2
                coord = [x, y]
                angle = calculate_angle(data["right_wrist"][i], data["right_elbow"][i], coord)
                ewa_ra_list.append(angle)

        # elbow-wrist-pinky left arm
        if ((data["left_elbow"][i] != None) and (data["left_wrist"][i] != None) and (data["left_pinky"][i] != None)):
            angle = calculate_angle(data["left_wrist"][i], data["left_elbow"][i], data["left_pinky"][i])
            ewp_la_list.append(angle)
        
    hew_ra = get_parameters(hew_ra_list)
    hew_la = get_parameters(hew_la_list)
    sew_ra = get_parameters(sew_ra_list)
    sew_la = get_parameters(sew_la_list)
    ewa_ra = get_parameters(ewa_ra_list)
    ewp_la = get_parameters(ewp_la_list)
    # print(hew_la_list)
    return hew_ra, hew_la, sew_ra, sew_la, ewa_ra, ewp_la

def get_parameters(angles, max_val=180):
    """
    Calculates distribution parameters for a given set of values by scaling
    them to the [0,1] interval and fitting a Beta distribution.
    
    Inputs:
        angles  = numpy array of values (in degrees by default; for ratios, adjust max_val)
        max_val = maximum value (default is 180 for angles; for ratios use 1)
    
    Outputs:
        A dictionary containing:
            - mean: sample mean
            - std: sample standard deviation
            - alpha: Beta distribution alpha parameter
            - beta: Beta distribution beta parameter
    """
    angles = np.array(angles)
    mean_val = float(np.mean(angles))
    std_val = float(np.std(angles))
    m_y = mean_val / max_val
    s_y_sq = (std_val**2) / (max_val**2)
    # print(angles)
    # print(f"s_y_sq: {s_y_sq}")

    if s_y_sq <= 0:
        alpha = beta_val = 100
    else:
        factor = (m_y * (1 - m_y) / s_y_sq) - 1
        # print(f"my: {m_y}")
        # print(f"factor: {factor}")
        alpha = m_y * factor
        beta_val = (1 - m_y) * factor
    
    return {"mean": mean_val, "std": std_val, "alpha": alpha, "beta": beta_val}

def generate_elbow_parameters(data):
    elbows_list = []
    
    if (data["right_wrist"][0] != None and data["right_elbow"][0] != None):
        arm_length = math.sqrt((data["right_wrist"][0][0] - data["right_elbow"][0][0])**2 + (data["right_wrist"][0][1] - data["right_elbow"][0][1])**2)
    else:
        arm_length = math.sqrt((data["left_wrist"][0][0] - data["left_elbow"][0][0])**2 + (data["left_wrist"][0][1] - data["left_elbow"][0][1])**2)

    for i in range(len(data["left_elbow"])):
        if (data["left_elbow"][i] != None) and (data["right_elbow"][i] != None):
            left_entry = data["left_elbow"][i]
            right_entry = data["right_elbow"][i]
            elbows_list.append(abs(((left_entry[1]) - (right_entry[1])) / arm_length))

    elbows = np.array(elbows_list)
    print(f"elbow diff list = {elbows_list}")
    if len(elbows > 0):
        mean_val = float(np.mean(elbows))
        std_val = float(np.std(elbows))
    else:
        mean_val = 0.0
        std_val = 0.0
    
    m_y = mean_val  
    s_y_sq = std_val**2
    
    # Compute Beta distribution parameters.
    if s_y_sq <= 0:
        alpha = beta_val = 100  # default for very low variance
    else:
        factor = (m_y * (1 - m_y) / s_y_sq) - 1
        alpha = m_y * factor
        beta_val = (1 - m_y) * factor


    return {"mean": mean_val, "std": std_val, "alpha": alpha, "beta": beta_val}

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
            # Extract player ID and position (e.g., klay_front_01 waist)
            # Updated regex to match klay_front_## or klay_side_ra_## followed by position
            # match = re.match(r'(klay_(?:front|side_ra)_\d+)\s+(\w+):\s+(.+)', entry)
            match = re.match(r'(klay_front_\d+)\s+(\w+):\s+(.+)', entry)
            if not match:
                print(f"Skipping entry, no match: {entry[:50]}...")
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
            
            # Ensure data_dict is a dictionary, not None
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
            elif position.lower() == 'max_hand':  # Updated to match data
                hand_data.append(data_dict)
            else:
                print(f"Unknown position '{position}' in entry: {entry[:50]}...")
                    
        except Exception as e:
            print(f"Error processing entry: {entry[:50]}... Error: {e}")
            continue
    
    return waist_data, eye_data, hand_data

def main():
    # Parse data from data_klay.txt
    with open('data_klay_new_std.txt', 'r') as file:
        file_content = file.read()
    
    # Parse the data
    waist_data, eye_data, hand_data = parse_data(file_content)
        
    w_data = prep_data(waist_data)
    e_data = prep_data(eye_data)
    m_data = prep_data(hand_data)

    print("Waist Data:", len(w_data['left_shoulder']), "entries")
    print("Eye Data:", len(e_data['left_shoulder']), "entries")
    print("Hand Data:", len(m_data['left_shoulder']), "entries")

    data = w_data
    name = "MAX"
    # generate parameters
    sc_f_hew_ra, sc_f_hew_la, sc_f_sew_ra, sc_f_sew_la, sc_f_ewa_ra, sc_f_ewp_la = generate_front_parameters(data)
    sc_f_elbow = generate_elbow_parameters(data)
    
    # print parameters
    print(f"{name}_F_ELBOW_DIFF: {sc_f_elbow}")
    print(f"{name}_F_EWA_RA: {sc_f_ewa_ra}")
    print(f"{name}_F_EWP_LA: {sc_f_ewp_la}")
    print(f"{name}_F_HEW_RA: {sc_f_hew_ra}")
    print(f"{name}_F_HEW_LA: {sc_f_hew_la}")
    print(f"{name}_F_SEW_RA: {sc_f_sew_ra}")
    print(f"{name}_F_SEW_LA: {sc_f_sew_la}")
    
    
    # plot
    # plot_beta_distribution(sc_f_ewa_ra, name + "_F_EWA_RA")
    # plot_beta_distribution(sc_f_ewp_la, name + "_F_EWP_LA")
    # plot_beta_distribution(sc_f_hew_ra, name + "_F_HEW_RA")
    # plot_beta_distribution(sc_f_hew_la, name + "_F_HEW_LA")
    # plot_beta_distribution(sc_f_sew_ra, name + "_F_SEW_RA")
    # plot_beta_distribution(sc_f_sew_la, name + "_F_SEW_LA")
    # plot_beta_distribution(sc_f_elbow, name + "_F_ELBOW_DIFF")

if __name__ == "__main__":
    main()
