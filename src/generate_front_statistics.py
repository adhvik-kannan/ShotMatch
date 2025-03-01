from scipy.stats import beta
import math
import numpy as np
import matplotlib.pyplot as plt

def plot_beta_with_point(new_angle, params, label="Beta Distribution", save_filename=None):
    """
    Plots the Beta distribution (scaled to [0,180]) for the given parameters and marks
    the new angle value on the plot.
    
    Inputs:
      new_angle: float, the new data point (angle in degrees) to mark.
      params: dict, Beta distribution parameters in the format
              {"mean": mean_val, "std": std_val, "alpha": alpha_val, "beta": beta_val}
      label: string, title/label for the plot.
      save_filename: if provided, the plot will be saved to this file.
    """
    # Generate x-values over the range [0, 180].
    x = np.linspace(0, 180, 300)
    # Compute the Beta PDF scaled to [0,180]:
    y = (1/180.0) * beta.pdf(x/180.0, params["alpha"], params["beta"])
    
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, label=f"Beta({params['alpha']:.2f}, {params['beta']:.2f})", color="blue")
    
    # Mark the new data point:
    # Compute PDF value at new_angle
    new_val = (1/180.0) * beta.pdf(new_angle/180.0, params["alpha"], params["beta"])
    plt.axvline(new_angle, color="red", linestyle="--", label=f"New Angle: {new_angle:.1f}°")
    plt.scatter([new_angle], [new_val], color="red", zorder=5)
    
    plt.xlabel("Angle (degrees)")
    plt.ylabel("Density")
    plt.title(label)
    plt.legend()
    plt.grid(True)
    
    if save_filename:
        plt.savefig(save_filename)
    
    plt.show()

def calculate_angle(vertex, a, b):
    """
    Calculate the angle (in degrees) between three points: a -> vertex -> b.
    
    Inputs:
        a       = point 1 (e.g., hip for hew, shoulder for sew, or elbow for ewp)
        vertex  = point 2 (e.g., shoulder for hew, elbow for sew, or wrist for ewp)
        b       = point 3 (e.g., elbow for hew, wrist for sew, or pinky for ewp)
    
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

def get_elbow(data):
    if (data["right_wrist"][0] != None and data["right_elbow"][0] != None):
        arm_length = math.sqrt((data["right_wrist"][0] - data["right_elbow"][0])**2 + (data["right_wrist"][1] - data["right_elbow"][1])**2)
    elif (data["left_wrist"][0] != None and data["left_elbow"][0] != None):
        arm_length = math.sqrt((data["left_wrist"][0] - data["left_elbow"][0])**2 + (data["left_wrist"][1] - data["left_elbow"][1])**2)
    else: 
        print("ERROR: elbow/wrist joints cannot be detected")
        return -1
    
    if (data["left_elbow"] != None) and (data["right_elbow"] != None):
        left_entry = data["left_elbow"]
        right_entry = data["right_elbow"]
        return (abs(((left_entry[1]) - (right_entry[1])) / arm_length))

def compare_front(data, hew_ra_params, hew_la_params, sew_ra_params, sew_la_params, ewa_ra_params, ewp_la_params, elbow_params):
    # hip-elbow-wrist right arm
    if ((data["right_hip"] != None) and (data["right_wrist"] != None) and (data["right_elbow"] != None)):
        angle_hew_ra = calculate_angle(data["right_elbow"], data["right_hip"], data["right_wrist"])
    
    # hip-elbow-wrist left arm
    if ((data["left_hip"] != None) and (data["left_wrist"] != None) and (data["left_elbow"] != None)):
        angle_hew_la = calculate_angle(data["left_elbow"], data["left_hip"], data["left_wrist"])

    # shoulder-elbow-wrist right arm
    if ((data["right_shoulder"] != None) and (data["right_elbow"] != None) and (data["right_wrist"] != None)):
        angle_sew_ra = calculate_angle(data["right_elbow"], data["right_shoulder"], data["right_wrist"])
    
    # shoulder-elbow-wrist left arm
    if ((data["left_shoulder"] != None) and (data["left_elbow"] != None) and (data["left_wrist"] != None)):
        angle_sew_la = calculate_angle(data["left_elbow"], data["left_shoulder"], data["left_wrist"])
    
    # elbow-wrist-average right arm (avg = thumb and pinky)
    if ((data["right_elbow"] != None) and (data["right_wrist"] != None)):
        if (data["right_pinky"] != None and data["right_thumb"] != None):
            x = (data["right_pinky"][0] + data["right_thumb"][0]) / 2
            y = (data["right_pinky"][1] + data["right_thumb"][1]) / 2
            coord = [x, y]
            angle_ewa_ra = calculate_angle(data["right_wrist"], data["right_elbow"], coord)

    # elbow-wrist-pinky left arm
    if ((data["left_elbow"] != None) and (data["left_wrist"] != None) and (data["left_pinky"] != None)):
        angle_ewp_la = calculate_angle(data["left_wrist"], data["left_elbow"], data["left_pinky"])
    
    # hew: Angle at shoulder using points: hip, shoulder, left_elbow.
    pdf_hew_ra_new = beta.pdf(angle_hew_ra/180.0, hew_ra_params["alpha"], hew_ra_params["beta"])
    pdf_hew_la_new = beta.pdf(angle_hew_la/180.0, hew_la_params["alpha"], hew_la_params["beta"])
    pdf_hew_ra_mean = beta.pdf(hew_ra_params["mean"]/180.0, hew_ra_params["alpha"], hew_ra_params["beta"])
    pdf_hew_la_mean = beta.pdf(hew_la_params["mean"]/180.0, hew_la_params["alpha"], hew_la_params["beta"])
    score_hew_ra = (pdf_hew_ra_new / pdf_hew_ra_mean) * 100 if pdf_hew_ra_mean != 0 else 0
    score_hew_la = (pdf_hew_la_new / pdf_hew_la_mean) * 100 if pdf_hew_la_mean != 0 else 0
    score_hew_ra = max(0, min(100, score_hew_ra))
    score_hew_la = max(0, min(100, score_hew_la))
    
    # sew: Angle at left_elbow using points: shoulder, left_elbow, wrist.
    pdf_sew_ra_new = beta.pdf(angle_sew_ra/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    pdf_sew_la_new = beta.pdf(angle_sew_la/180.0, sew_la_params["alpha"], sew_la_params["beta"])
    pdf_sew_ra_mean = beta.pdf(sew_ra_params["mean"]/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    pdf_sew_la_mean = beta.pdf(sew_la_params["mean"]/180.0, sew_la_params["alpha"], sew_la_params["beta"])
    score_sew_ra = (pdf_sew_ra_new / pdf_sew_ra_mean) * 100 if pdf_sew_ra_mean != 0 else 0
    score_sew_la = (pdf_sew_la_new / pdf_sew_la_mean) * 100 if pdf_sew_la_mean != 0 else 0
    score_sew_ra = max(0, min(100, score_sew_ra))
    score_sew_la = max(0, min(100, score_sew_la))
    
    # ewa: Angle at wrist using points: right elbow, wrist, average between thumb and pinky
    pdf_ewa_ra_new = beta.pdf(angle_ewa_ra/180.0, ewa_ra_params["alpha"], ewa_ra_params["beta"])
    pdf_ewa_ra_mean = beta.pdf(ewa_ra_params["mean"]/180.0, ewa_ra_params["alpha"], ewa_ra_params["beta"])
    score_ewa_ra = (pdf_ewa_ra_new / pdf_ewa_ra_mean) * 100 if pdf_ewa_ra_mean != 0 else 0
    score_ewa_ra = max(0, min(100, score_ewa_ra))

    # ewp: Angle at wrist using points: left_elbow, wrist, pinky.
    pdf_ewp_la_new = beta.pdf(angle_ewp_la/180.0, ewp_la_params["alpha"], ewp_la_params["beta"])
    pdf_ewp_la_mean = beta.pdf(ewp_la_params["mean"]/180.0, ewp_la_params["alpha"], ewp_la_params["beta"])
    score_ewp_la = (pdf_ewp_la_new / pdf_ewp_la_mean) * 100 if pdf_ewp_la_mean != 0 else 0
    score_ewp_la = max(0, min(100, score_ewp_la))
    
    # ec: Use the calculate_elbow function.
    ec_value = get_elbow(data)

    # For ec, values are already in [0,1], so no scaling is needed.
    pdf_ec_new = beta.pdf(ec_value, elbow_params["alpha"], elbow_params["beta"])
    pdf_ec_mean = beta.pdf(elbow_params["mean"], elbow_params["alpha"], elbow_params["beta"])
    score_ec = (pdf_ec_new / pdf_ec_mean) * 100 if pdf_ec_mean != 0 else 0
    score_ec = max(0, min(100, score_ec))
    
    plot_beta_with_point(angle_hew_ra, hew_ra_params, label="HEW_RA")
    plot_beta_with_point(angle_hew_la, hew_la_params, label="HEW_LA")
    plot_beta_with_point(angle_sew_ra, sew_ra_params, label="SEW_RA")
    plot_beta_with_point(angle_sew_la, sew_la_params, label="SEW_LA")
    plot_beta_with_point(angle_ewa_ra, ewa_ra_params, label="EWA_RA")
    plot_beta_with_point(angle_ewp_la, ewp_la_params, label="EWP_LA")

    return {
        "hew_ra_score": score_hew_ra,
        "hew_la_score": score_hew_la,
        "sew_ra_score": score_sew_ra,
        "sew_la_score": score_sew_la,
        "ewa_ra_score": score_ewa_ra,
        "ewp_la_score": score_ewp_la,
        "ec_score": score_ec
    }

def get_klay_data():
    return {'left_shoulder': [654, 518], 'right_shoulder': [373, 476], 'left_elbow': [750, 323], 'right_elbow': [431, 291], 'left_wrist': [685, 584], 'right_wrist': [544, 570], 'left_hip': [651, 53], 'right_hip': [446, 51], 'left_pinky': [668, 656], 'right_pinky': [562, 633], 'left_thumb': [660, 641], 'right_thumb': [549, 624], 'ball': None, 'Side': 'FRONT', 'frame': 18}

def get_params():
    hew_ra_params = {'mean': 162.06345930992, 'std': 8.983861762318169, 'alpha': 31.526908690697145, 'beta': 3.4892731709603337}
    hew_la_params = {'mean': 144.18126862048007, 'std': 13.186107496883794, 'alpha': 22.99051113208135, 'beta': 5.711497411536249}
    sew_ra_params = {'mean': 56.513779392939966, 'std': 43.3325881553567, 'alpha': 0.8529125252622869, 'beta': 1.8636683899824433}
    sew_la_params = {'mean': 69.94910046694802, 'std': 25.983045238195032, 'alpha': 4.0424297033764995, 'beta': 6.359953483117646}
    ewa_ra_params = {'mean': 171.2429226074844, 'std': 2.700463421634448, 'alpha': 194.67860198702382, 'beta': 9.955538940285523}
    ewp_la_params = {'mean': 166.53889329592488, 'std': 9.400764569916712, 'alpha': 22.544792995353788, 'beta': 1.8222642058302212}
    elbow_params = {'mean': 0.1860944586520072, 'std': 0.07193177550894218, 'alpha': 5.261431738885052, 'beta': 23.011477497621666}

    return hew_ra_params, hew_la_params, sew_ra_params, sew_la_params, ewa_ra_params, ewp_la_params, elbow_params
def main():
    # Compute similarity scores for front view.
    new_front_data = get_klay_data()
    hew_ra_params, hew_la_params, sew_ra_params, sew_la_params, ewa_ra_params, ewp_la_params, elbow_params = get_params()
    front_scores = compare_front(new_front_data, hew_ra_params, hew_la_params, sew_ra_params, sew_la_params, ewa_ra_params, ewp_la_params, elbow_params)
    
    print("Front view similarity scores:")
    print(front_scores)

if __name__ == "__main__":
    main()
