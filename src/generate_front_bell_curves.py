import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import beta

NUM_CLIPS = 0

def calculate_angle(vertex, a, b):
    """
    Calculate the angle (in degrees) between three points: a -> vertex -> b.
    
    Inputs:
        a       = point 1 (e.g., hip for hse, shoulder for sew, or elbow for ewp)
        vertex  = point 2 (e.g., shoulder for hse, elbow for sew, or wrist for ewp)
        b       = point 3 (e.g., elbow for hse, wrist for sew, or pinky for ewp)
    
    Output:
        Angle in degrees between a -> vertex -> b.
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

def process_front_data(hip, shoulder, left_elbow, right_elbow, wrist, pinky):
    """
    Processes frames of front-view data and computes four arrays:
      - hse: Hip -> Shoulder -> Elbow angles (vertex = shoulder)
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
        hse_array, sew_array, ewp_array, ec_array as numpy arrays.
    """
    hse_list = []
    sew_list = []
    ewp_list = []
    ec_list = []
    
    for i in range(len(hip)):
        h = hip[i]
        s = shoulder[i]
        le = left_elbow[i]
        re = right_elbow[i]
        w = wrist[i]
        p = pinky[i]
        
        # Hip-Shoulder-Elbow (hse): angle at shoulder using points: hip, shoulder, left_elbow.
        angle_hse = calculate_angle(s, h, le)
        hse_list.append(angle_hse)
        
        # Shoulder-Elbow-Wrist (sew): angle at left_elbow using points: shoulder, left_elbow, wrist.
        angle_sew = calculate_angle(le, s, w)
        sew_list.append(angle_sew)
        
        # Elbow-Wrist-Pinky (ewp): angle at wrist using points: left_elbow, wrist, pinky.
        angle_ewp = calculate_angle(w, le, p)
        ewp_list.append(angle_ewp)
        
    
    return np.array(hse_list), np.array(sew_list), np.array(ewp_list)

def calculate_distribution_parameters(angles, max_val=180):
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
    mean_val = float(np.mean(angles))
    std_val = float(np.std(angles))
    m_y = mean_val / max_val
    s_y_sq = (std_val**2) / (max_val**2)
    
    if s_y_sq <= 0:
        alpha = beta_val = 100
    else:
        factor = (m_y * (1 - m_y) / s_y_sq) - 1
        alpha = m_y * factor
        beta_val = (1 - m_y) * factor
    
    return {"mean": mean_val, "std": std_val, "alpha": alpha, "beta": beta_val}

def generate_elbow_parameters(data):
    elbows_list = []
    
    if (data["right_wrist"][0] != "NONE" and data["right_elbow"][0] != "NONE"):
        arm_length = math.sqrt((data["right_wrist"][0][0] - data["right_elbow"][0][0])**2 + (data["right_wrist"][0][1] - data["right_elbow"][0][1])**2)
    else:
        arm_length = math.sqrt((data["left_wrist"][0][0] - data["left_elbow"][0][0])**2 + (data["left_wrist"][0][1] - data["left_elbow"][0][1])**2)

    for i in range(len(data["left_elbow"])):
        if (data["left_elbow"][i] != "NONE") and (data["right_elbow"][i] != "NONE"):
            left_entry = data["left_elbow"][i]
            right_entry = data["right_elbow"][i]
            elbows_list.append(abs(((left_entry[1]) - (right_entry[1])) / arm_length))

    elbows = np.array(elbows_list)
    # print(f"elbow diff list: {elbows_list}")
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

def plot_beta_distribution(params):
    alpha = params["alpha"]
    beta_val = params["beta"]

    # Generate x values between 0 and 1
    x = np.linspace(0, 2, 100)

    # Compute the Beta probability density function (PDF)
    y = beta.pdf(x, alpha, beta_val)

    # Plot the distribution
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, label=f'Beta({alpha:.2f}, {beta_val:.2f})', color='b')
    plt.fill_between(x, y, alpha=0.3, color='blue')  # Fill under the curve
    plt.xlabel('x')
    plt.ylabel('Density')
    plt.title('Beta Distribution')
    plt.legend()
    plt.grid()

    # Show the plot
    plt.show()

def get_steph_curry_front_data():
    nba_18 = {'left_shoulder': [191, 466], 'right_shoulder': [125, 468], 'left_elbow': [215, 472], 'right_elbow': [136, 459], 'left_wrist': [205, 535], 'right_wrist': [152, 527], 'left_hip': [182, 326], 'right_hip': [140, 327], 'ball': None, 'Side': 'FRONT', 'frame': 63}
    nba_19 = {'left_shoulder': [436, 656], 'right_shoulder': [362, 662], 'left_elbow': [474, 618], 'right_elbow': [352, 633], 'left_wrist': [460, 636], 'right_wrist': [380, 695], 'left_hip': [425, 521], 'right_hip': [382, 525], 'ball': None, 'Side': 'FRONT', 'frame': 45}
    nba_20 = {'left_shoulder': [168, 533], 'right_shoulder': [101, 538], 'left_elbow': [196, 528], 'right_elbow': [108, 517], 'left_wrist': [184, 592], 'right_wrist': [127, 575], 'left_hip': [156, 391], 'right_hip': [113, 393], 'ball': None, 'Side': 'FRONT', 'frame': 15}
    nba_22 = {'left_shoulder': [271, 508], 'right_shoulder': [207, 510], 'left_elbow': [313, 511], 'right_elbow': [218, 529], 'left_wrist': [277, 567], 'right_wrist': [227, 589], 'left_hip': [271, 363], 'right_hip': [228, 367], 'ball': None, 'Side': 'FRONT', 'frame': 37}
    nba_23 = {'left_shoulder': [241, 610], 'right_shoulder': [173, 615], 'left_elbow': [271, 615], 'right_elbow': [176, 595], 'left_wrist': [254, 676], 'right_wrist': [196, 662], 'left_hip': [224, 469], 'right_hip': [182, 473], 'ball': None, 'Side': 'FRONT', 'frame': 19}
    nba_24 = {'left_shoulder': [132, 747], 'right_shoulder': [63, 747], 'left_elbow': [161, 745], 'right_elbow': [73, 736], 'left_wrist': [145, 810], 'right_wrist': [88, 800], 'left_hip': [118, 603], 'right_hip': [74, 605], 'ball': None, 'Side': 'FRONT', 'frame': 11}
    nba_26 = {'left_shoulder': [256, 666], 'right_shoulder': [186, 675], 'left_elbow': [294, 669], 'right_elbow': [201, 666], 'left_wrist': [277, 731], 'right_wrist': [214, 732], 'left_hip': [242, 513], 'right_hip': [195, 516], 'ball': None, 'Side': 'FRONT', 'frame': 21}
    nba_27 = {'left_shoulder': [263, 723], 'right_shoulder': [192, 728], 'left_elbow': [290, 729], 'right_elbow': [198, 714], 'left_wrist': [277, 796], 'right_wrist': [216, 787], 'left_hip': [245, 570], 'right_hip': [199, 574], 'ball': None, 'Side': 'FRONT', 'frame': 10}

    merged_dict = {}

    for d in [nba_18, nba_19, nba_20, nba_22, nba_23, nba_24, nba_26, nba_27]:
        for key, value in d.items():
            if key not in merged_dict:
                merged_dict[key] = [value]
            else:
                merged_dict[key].append(value)

    return merged_dict

def main():
    sc_f_data = get_steph_curry_front_data()
    sc_f_data = generate_elbow_parameters(sc_f_data)
    print("\nSteph Curry Front-Elbow Params: ", sc_f_data)

    # plot_beta_distribution(sc_f_data)

if __name__ == "__main__":
    main()
