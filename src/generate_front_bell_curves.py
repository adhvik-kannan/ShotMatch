import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import beta

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
    print(angles)
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
    # print(f"elbow diff list = {elbows_list}")
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
    print(f"params: {params}")
    alpha = params["alpha"]
    beta_val = params["beta"]

    # Generate x values between 0 and 1
    x = np.linspace(0, 1, 100)

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
    nba_18 = {'left_shoulder': [191, 466], 'right_shoulder': [125, 468], 'left_elbow': [215, 472], 'right_elbow': [136, 459], 'left_wrist': [205, 535], 'right_wrist': [152, 527], 'left_hip': [182, 326], 'right_hip': [140, 327], 'left_pinky': [198, 549], 'right_pinky': [159, 543], 'left_thumb': [197, 543], 'right_thumb': [156, 538], 'ball': None, 'Side': 'FRONT', 'frame': 63}
    nba_19 = {'left_shoulder': [436, 656], 'right_shoulder': [362, 662], 'left_elbow': [474, 618], 'right_elbow': [352, 633], 'left_wrist': [460, 636], 'right_wrist': [380, 695], 'left_hip': [425, 521], 'right_hip': [382, 525], 'left_pinky': [454, 638], 'right_pinky': [389, 711], 'left_thumb': [446, 643], 'right_thumb': [387, 708], 'ball': None, 'Side': 'FRONT', 'frame': 45}
    nba_20 = {'left_shoulder': [168, 533], 'right_shoulder': [101, 538], 'left_elbow': [196, 528], 'right_elbow': [108, 517], 'left_wrist': [184, 592], 'right_wrist': [127, 575], 'left_hip': [156, 391], 'right_hip': [113, 393], 'left_pinky': [179, 609], 'right_pinky': [132, 595], 'left_thumb': [177, 606], 'right_thumb': [130, 595], 'ball': None, 'Side': 'FRONT', 'frame': 15}
    nba_22 = {'left_shoulder': [271, 508], 'right_shoulder': [207, 510], 'left_elbow': [313, 511], 'right_elbow': [218, 529], 'left_wrist': [277, 567], 'right_wrist': [227, 589], 'left_hip': [271, 363], 'right_hip': [228, 367], 'left_pinky': [270, 583], 'right_pinky': [232, 606], 'left_thumb': [266, 578], 'right_thumb': [231, 597], 'ball': None, 'Side': 'FRONT', 'frame': 37}
    nba_23 = {'left_shoulder': [241, 610], 'right_shoulder': [173, 615], 'left_elbow': [271, 615], 'right_elbow': [176, 595], 'left_wrist': [254, 676], 'right_wrist': [196, 662], 'left_hip': [224, 469], 'right_hip': [182, 473], 'left_pinky': [250, 691], 'right_pinky': [200, 684], 'left_thumb': [246, 688], 'right_thumb': [194, 678], 'ball': None, 'Side': 'FRONT', 'frame': 19}
    nba_24 = {'left_shoulder': [132, 747], 'right_shoulder': [63, 747], 'left_elbow': [161, 745], 'right_elbow': [73, 736], 'left_wrist': [145, 810], 'right_wrist': [88, 800], 'left_hip': [118, 603], 'right_hip': [74, 605], 'left_pinky': [136, 826], 'right_pinky': [96, 816], 'left_thumb': [134, 823], 'right_thumb': [90, 811], 'ball': None, 'Side': 'FRONT', 'frame': 11}
    nba_26 = {'left_shoulder': [256, 666], 'right_shoulder': [186, 675], 'left_elbow': [294, 669], 'right_elbow': [201, 666], 'left_wrist': [277, 731], 'right_wrist': [214, 732], 'left_hip': [242, 513], 'right_hip': [195, 516], 'left_pinky': [269, 749], 'right_pinky': [217, 750], 'left_thumb': [266, 744], 'right_thumb': [213, 744], 'ball': None, 'Side': 'FRONT', 'frame': 21}
    nba_27 = {'left_shoulder': [263, 723], 'right_shoulder': [192, 728], 'left_elbow': [290, 729], 'right_elbow': [198, 714], 'left_wrist': [277, 796], 'right_wrist': [216, 787], 'left_hip': [245, 570], 'right_hip': [199, 574], 'left_pinky': [267, 815], 'right_pinky': [217, 805], 'left_thumb': [267, 809], 'right_thumb': [217, 802], 'ball': None, 'Side': 'FRONT', 'frame': 10}

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

    sc_f_hew_ra, sc_f_hew_la, sc_f_sew_ra, sc_f_sew_la, sc_f_ewa_ra, sc_f_ewp_la = generate_front_parameters(sc_f_data)
    sc_f_elbow = generate_elbow_parameters(sc_f_data)
    print("\nSteph Curry Front-hew-ra params: ", sc_f_hew_ra)
    print("\nSteph Curry Front-hew-la params: ", sc_f_hew_la)
    print("\nSteph Curry Front-sew-ra params: ", sc_f_sew_ra)
    print("\nSteph Curry Front-sew-la params: ", sc_f_sew_la)
    print("\nSteph Curry Front-ewa-ra params: ", sc_f_ewa_ra)
    print("\nSteph Curry Front-ewp-la params: ", sc_f_ewp_la)
    print("\nSteph Curry Front-Elbow Params: ", sc_f_elbow)

    plot_beta_distribution(sc_f_hew_ra)
    plot_beta_distribution(sc_f_hew_la)
    plot_beta_distribution(sc_f_sew_ra)
    plot_beta_distribution(sc_f_sew_la)
    plot_beta_distribution(sc_f_ewa_ra)
    plot_beta_distribution(sc_f_ewp_la)
    plot_beta_distribution(sc_f_elbow)
    

if __name__ == "__main__":
    main()
