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

def compare_side_ra(data, sew_ra_params, ewp_ra_params):
    # shoulder-elbow-wrist right arm
    if ((data["right_shoulder"] != None) and (data["right_elbow"] != None) and (data["right_wrist"] != None)):
        angle_sew_ra = calculate_angle(data["right_elbow"], data["right_shoulder"], data["right_wrist"])

    # elbow-wrist-pinky right arm
    if ((data["right_elbow"] != None) and (data["right_wrist"] != None) and (data["right_pinky"] != None)):
        angle_ewp_ra = calculate_angle(data["right_wrist"], data["right_elbow"], data["right_pinky"])
    
    # sew: Angle at left_elbow using points: shoulder, left_elbow, wrist.
    pdf_sew_ra_new = beta.pdf(angle_sew_ra/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    pdf_sew_ra_mean = beta.pdf(sew_ra_params["mean"]/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    score_sew_ra = (pdf_sew_ra_new / pdf_sew_ra_mean) * 100 if pdf_sew_ra_mean != 0 else 0
    score_sew_ra = max(0, min(100, score_sew_ra))
    
    # ewp: Angle at wrist using points: right_elbow, wrist, pinky.
    pdf_ewp_ra_new = beta.pdf(angle_ewp_ra/180.0, ewp_ra_params["alpha"], ewp_ra_params["beta"])
    pdf_ewp_ra_mean = beta.pdf(ewp_ra_params["mean"]/180.0, ewp_ra_params["alpha"], ewp_ra_params["beta"])
    score_ewp_ra = (pdf_ewp_ra_new / pdf_ewp_ra_mean) * 100 if pdf_ewp_ra_mean != 0 else 0
    score_ewp_ra = max(0, min(100, score_ewp_ra))

    plot_beta_with_point(angle_sew_ra, sew_ra_params, label="SEW")
    plot_beta_with_point(angle_ewp_ra, ewp_ra_params, label="EWP")

    return {
        "sew_ra_score": score_sew_ra,
        "ewp_ra_score": score_ewp_ra,
    }

def compare_side_la(data, sew_la_params, ewa_la_params):
    # shoulder-elbow-wrist left arm
    if ((data["left_shoulder"] != None) and (data["left_elbow"] != None) and (data["left_wrist"] != None)):
        angle_sew_la = calculate_angle(data["left_elbow"], data["left_shoulder"], data["left_wrist"])

    # elbow-wrist-average left arm (avg = thumb and pinky)
    if ((data["left_elbow"] != None) and (data["left_wrist"] != None)):
        if (data["left_pinky"] != None and data["left_thumb"] != None):
            x = (data["left_pinky"][0] + data["left_thumb"][0]) / 2
            y = (data["left_pinky"][1] + data["left_thumb"][1]) / 2
            coord = [x, y]
            angle_ewa_la = calculate_angle(data["left_wrist"], data["left_elbow"], coord)

    
    # sew: Angle at left_elbow using points: shoulder, left_elbow, wrist.
    pdf_sew_la_new = beta.pdf(angle_sew_la/180.0, sew_la_params["alpha"], sew_la_params["beta"])
    pdf_sew_la_mean = beta.pdf(sew_la_params["mean"]/180.0, sew_la_params["alpha"], sew_la_params["beta"])
    score_sew_la = (pdf_sew_la_new / pdf_sew_la_mean) * 100 if pdf_sew_la_mean != 0 else 0
    score_sew_la = max(0, min(100, score_sew_la))
    
    # ewa: Angle at wrist using points: left elbow, wrist, average between thumb and pinky
    pdf_ewa_la_new = beta.pdf(angle_ewa_la/180.0, ewa_la_params["alpha"], ewa_la_params["beta"])
    pdf_ewa_la_mean = beta.pdf(ewa_la_params["mean"]/180.0, ewa_la_params["alpha"], ewa_la_params["beta"])
    score_ewa_la = (pdf_ewa_la_new / pdf_ewa_la_mean) * 100 if pdf_ewa_la_mean != 0 else 0
    score_ewa_la = max(0, min(100, score_ewa_la))
    
    return {
        "sew_la_score": score_sew_la,
        "ewa_la_score": score_ewa_la
    }

def get_klay_data():
    return {'left_shoulder': [805, 735], 'right_shoulder': [821, 737], 'left_elbow': None, 'right_elbow': [927, 758], 'left_wrist': None, 'right_wrist': [899, 838], 'left_hip': [779, 531], 'right_hip': [787, 533], 'left_pinky': None, 'right_pinky': [886, 862], 'left_thumb': None, 'right_thumb': [874, 847], 'ball': None, 'Side': 'RIGHT', 'frame': 52}

def get_ra_params():
    sew_ra_params = {'mean': 80.85076856368889, 'std': 15.340129920993972, 'alpha': 14.852084900953656, 'beta': 18.213466975226094}
    ewp_ra_params = {'mean': 168.20268550842667, 'std': 7.730845782832074, 'alpha': 30.091304505321396, 'beta': 2.1105286258535343}
    return sew_ra_params, ewp_ra_params

def main():
    side_ra_data = get_klay_data()
    sew_ra_params, ewp_ra_params = get_ra_params()
    side_ra_scores = compare_side_ra(side_ra_data, sew_ra_params, ewp_ra_params)

    print("Side View RA similarity scores:")
    print(side_ra_scores)

if __name__ == "__main__":
    main()