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
    
    for i in range(len(data["ball"])):
        # shoulder-elbow-wrist right arm
        if ((data["right_shoulder"][i] != None) and (data["right_elbow"][i] != None) and (data["right_wrist"][i] != None)):
            angle = calculate_angle(data["right_elbow"][i], data["right_shoulder"][i], data["right_wrist"][i])
            sew_ra_list.append(angle)
        
        # elbow-wrist-pinky right arm
        if ((data["right_elbow"][i] != None) and (data["right_wrist"][i] != None) and (data["right_pinky"][i] != None)):
            angle = calculate_angle(data["right_wrist"][i], data["right_elbow"][i], data["right_pinky"][i])
            ewp_ra_list.append(angle)
    
    sew_ra = get_parameters(sew_ra_list)
    ewp_ra = get_parameters(ewp_ra_list)

    return sew_ra, ewp_ra

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


def get_steph_curry_s_ra_data():
    """
    manual steph data for generating his params
    """
    nba_1 = {'left_shoulder': [323, 733], 'right_shoulder': [408, 775], 'left_elbow': None, 'right_elbow': [495, 786], 'left_wrist': None, 'right_wrist': [454, 855], 'left_hip': [343, 538], 'right_hip': [399, 539], 'left_pinky': None, 'right_pinky': [448, 884], 'left_thumb': None, 'right_thumb': [440, 858], 'ball': None, 'Side': 'RIGHT', 'frame': 38}
    nba_2 = {'left_shoulder': [260, 724], 'right_shoulder': [367, 760], 'left_elbow': None, 'right_elbow': [468, 767], 'left_wrist': None, 'right_wrist': [419, 843], 'left_hip': [291, 504], 'right_hip': [357, 501], 'left_pinky': None, 'right_pinky': [413, 874], 'left_thumb': None, 'right_thumb': [399, 858], 'ball': None, 'Side': 'RIGHT', 'frame': 81}
    nba_4 = {'left_shoulder': [66, 656], 'right_shoulder': [-22, 657], 'left_elbow': None, 'right_elbow': [34, 665], 'left_wrist': [137, 685], 'right_wrist': [77, 743], 'left_hip': [61, 455], 'right_hip': [-1, 449], 'left_pinky': [144, 692], 'right_pinky': [91, 760], 'left_thumb': [134, 698], 'right_thumb': [79, 760], 'ball': None, 'Side': 'RIGHT', 'frame': 124}
    nba_5 = {'left_shoulder': [249, 692], 'right_shoulder': [345, 737], 'left_elbow': None, 'right_elbow': [448, 735], 'left_wrist': None, 'right_wrist': [415, 812], 'left_hip': [273, 486], 'right_hip': [328, 489], 'left_pinky': None, 'right_pinky': [401, 841], 'left_thumb': None, 'right_thumb': [393, 820], 'ball': None, 'Side': 'RIGHT', 'frame': 35}
    nba_6 = {'left_shoulder': [229, 688], 'right_shoulder': [300, 725], 'left_elbow': None, 'right_elbow': [386, 739], 'left_wrist': None, 'right_wrist': [370, 797], 'left_hip': [254, 504], 'right_hip': [297, 510], 'left_pinky': None, 'right_pinky': [365, 816], 'left_thumb': None, 'right_thumb': [347, 802], 'ball': None, 'Side': 'RIGHT', 'frame': 22}
    nba_7 = {'left_shoulder': [186, 728], 'right_shoulder': [279, 767], 'left_elbow': None, 'right_elbow': [369, 782], 'left_wrist': None, 'right_wrist': [345, 849], 'left_hip': [208, 523], 'right_hip': [266, 521], 'left_pinky': None, 'right_pinky': [327, 877], 'left_thumb': None, 'right_thumb': [317, 853], 'ball': None, 'Side': 'RIGHT', 'frame': 24}
    nba_8 = {'left_shoulder': [287, 682], 'right_shoulder': [340, 701], 'left_elbow': None, 'right_elbow': [422, 706], 'left_wrist': None, 'right_wrist': [406, 763], 'left_hip': [289, 499], 'right_hip': [322, 498], 'left_pinky': None, 'right_pinky': [390, 791], 'left_thumb': None, 'right_thumb': [378, 771], 'ball': None, 'Side': 'RIGHT', 'frame': 41}
    nba_9 = {'left_shoulder': [201, 661], 'right_shoulder': [263, 696], 'left_elbow': None, 'right_elbow': [343, 704], 'left_wrist': None, 'right_wrist': [337, 760], 'left_hip': [204, 476], 'right_hip': [243, 481], 'left_pinky': None, 'right_pinky': [343, 775], 'left_thumb': None, 'right_thumb': [320, 763], 'ball': None, 'Side': 'RIGHT', 'frame': 24}
    nba_10 = {'left_shoulder': [75, 709], 'right_shoulder': [138, 731], 'left_elbow': None, 'right_elbow': [222, 735], 'left_wrist': None, 'right_wrist': [193, 801], 'left_hip': [84, 530], 'right_hip': [120, 529], 'left_pinky': None, 'right_pinky': [190, 825], 'left_thumb': None, 'right_thumb': [179, 806], 'ball': None, 'Side': 'RIGHT', 'frame': 27}
    nba_11 = {'left_shoulder': [75, 488], 'right_shoulder': [91, 494], 'left_elbow': None, 'right_elbow': [148, 496], 'left_wrist': None, 'right_wrist': [151, 540], 'left_hip': [97, 364], 'right_hip': [100, 361], 'left_pinky': None, 'right_pinky': [152, 555], 'left_thumb': None, 'right_thumb': [143, 549], 'ball': None, 'Side': 'RIGHT', 'frame': 34}
    nba_12 = {'left_shoulder': [211, 552], 'right_shoulder': [223, 563], 'left_elbow': None, 'right_elbow': [282, 561], 'left_wrist': None, 'right_wrist': [263, 620], 'left_hip': [235, 412], 'right_hip': [223, 414], 'left_pinky': None, 'right_pinky': [260, 638], 'left_thumb': None, 'right_thumb': [253, 631], 'ball': None, 'Side': 'RIGHT', 'frame': 7}
    nba_13 = {'left_shoulder': [216, 545], 'right_shoulder': [214, 548], 'left_elbow': None, 'right_elbow': [264, 560], 'left_wrist': None, 'right_wrist': [248, 608], 'left_hip': [223, 415], 'right_hip': [220, 415], 'left_pinky': None, 'right_pinky': [245, 624], 'left_thumb': None, 'right_thumb': [233, 615], 'ball': None, 'Side': 'RIGHT', 'frame': 19}
    nba_14 = {'left_shoulder': [169, 556], 'right_shoulder': [140, 554], 'left_elbow': None, 'right_elbow': [180, 552], 'left_wrist': None, 'right_wrist': [183, 620], 'left_hip': [177, 415], 'right_hip': [152, 411], 'left_pinky': None, 'right_pinky': [179, 637], 'left_thumb': None, 'right_thumb': [178, 634], 'ball': None, 'Side': 'RIGHT', 'frame': 4}
    nba_15 = {'left_shoulder': [328, 520], 'right_shoulder': [332, 522], 'left_elbow': None, 'right_elbow': [388, 510], 'left_wrist': None, 'right_wrist': [394, 565], 'left_hip': [340, 397], 'right_hip': [341, 396], 'left_pinky': None, 'right_pinky': [399, 577], 'left_thumb': None, 'right_thumb': [392, 574], 'ball': None, 'Side': 'RIGHT', 'frame': 41}
    nba_16 = {'left_shoulder': [131, 595], 'right_shoulder': [130, 605], 'left_elbow': None, 'right_elbow': [177, 601], 'left_wrist': None, 'right_wrist': [173, 636], 'left_hip': [128, 473], 'right_hip': [128, 473], 'left_pinky': None, 'right_pinky': [174, 646], 'left_thumb': None, 'right_thumb': [170, 640], 'ball': None, 'Side': 'RIGHT', 'frame': 25}
    nba_17 = {'left_shoulder': [297, 647], 'right_shoulder': [298, 647], 'left_elbow': None, 'right_elbow': [372, 653], 'left_wrist': None, 'right_wrist': [339, 724], 'left_hip': [324, 459], 'right_hip': [319, 461], 'left_pinky': None, 'right_pinky': [330, 745], 'left_thumb': None, 'right_thumb': [319, 733], 'ball': None, 'Side': 'RIGHT', 'frame': 18}

    merged_dict = {}

    for d in [nba_1, nba_2, nba_4, nba_5, nba_6, nba_7, nba_8, nba_9, nba_10, nba_11, nba_12, nba_13, nba_14, nba_15, nba_16, nba_17]:
        for key, value in d.items():
            if key not in merged_dict:
                merged_dict[key] = [value]
            else:
                merged_dict[key].append(value)

    return merged_dict

def get_steph_curry_s_la_data():
    merged_dict = {}

    # for d in [nba_]:
    #     for key, value in d.items():
    #         if key not in merged_dict:
    #             merged_dict[key] = [value]
    #         else:
    #             merged_dict[key].append(value)

    return merged_dict

def main():
    sc_s_ra_data = get_steph_curry_s_ra_data()
    sc_s_la_data = get_steph_curry_s_la_data()

    sc_s_sew_ra, sc_s_ewp_ra = generate_side_ra_parameters(sc_s_ra_data)
    # sc_s_sew_la, sc_s_ewa_la = generate_side_la_parameters(sc_s_la_data)

    print("\nSteph Curry Side-sew-ra params: ", sc_s_sew_ra)
    # print("\nSteph Curry side-sew-la params: ", sc_s_sew_la)
    print("\nSteph Curry Side-ewp-ra params: ", sc_s_ewp_ra)
    # print("\nSteph Curry side-ewa-la params: ", sc_s_ewa_la)
    

if __name__ == "__main__":
    main()
