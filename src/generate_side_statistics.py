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

def compare_side_ra(data, ewp_ra_params, hse_ra_params, sew_ra_params):
    # shoulder-elbow-wrist right arm
    if(data == None):
        return {
            "Elbow->Wrist->Fingers Score (Right Arm)": 0,
            "Hip->Shoulder->Elbow Score (Right Arm)": 0,
            "Shoulder->Elbow->Wrist Score (Right Arm)": 0
        }
    if ((data["right_shoulder"] != None) and (data["right_elbow"] != None) and (data["right_wrist"] != None)):
        angle_sew_ra = calculate_angle(data["right_elbow"], data["right_shoulder"], data["right_wrist"])

    # elbow-wrist-pinky right arm
    if ((data["right_elbow"] != None) and (data["right_wrist"] != None) and (data["right_pinky"] != None)):
        angle_ewp_ra = calculate_angle(data["right_wrist"], data["right_elbow"], data["right_pinky"])
    
    # hip-shoulder-elbow right arm     
    if ((data["right_hip"] != None) and (data["right_shoulder"] != None) and (data["right_elbow"] != None)):
        angle_hse_ra = calculate_angle(data["right_shoulder"], data["right_hip"], data["right_elbow"])

    # print(f"Angle SEW RA: {angle_sew_ra}")
    # sew: Angle at left_elbow using points: shoulder, left_elbow, wrist.
    pdf_sew_ra_new = beta.pdf(angle_sew_ra/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    pdf_sew_ra_mean = beta.pdf(sew_ra_params["mean"]/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    score_sew_ra = (pdf_sew_ra_new / pdf_sew_ra_mean) * 100 if pdf_sew_ra_mean != 0 else 0
    score_sew_ra = math.ceil(max(0, min(100, score_sew_ra)))
    
    # ewp: Angle at wrist using points: right_elbow, wrist, pinky.
    pdf_ewp_ra_new = beta.pdf(angle_ewp_ra/180.0, ewp_ra_params["alpha"], ewp_ra_params["beta"])
    pdf_ewp_ra_mean = beta.pdf(ewp_ra_params["mean"]/180.0, ewp_ra_params["alpha"], ewp_ra_params["beta"])
    score_ewp_ra = (pdf_ewp_ra_new / pdf_ewp_ra_mean) * 100 if pdf_ewp_ra_mean != 0 else 0
    score_ewp_ra = math.ceil(max(0, min(100, score_ewp_ra)))

    # hse: Angle of arm during release using points: right_hip, shoulder, elbow
    pdf_hse_ra_new = beta.pdf(angle_hse_ra/180.0, hse_ra_params["alpha"], hse_ra_params["beta"])
    pdf_hse_ra_mean = beta.pdf(hse_ra_params["mean"]/180.0, hse_ra_params["alpha"], hse_ra_params["beta"])
    score_hse_ra = (pdf_hse_ra_new / pdf_hse_ra_mean) * 100 if pdf_hse_ra_mean != 0 else 0
    score_hse_ra = math.ceil(max(0, min(100, score_hse_ra)))

    plot_beta_with_point(angle_ewp_ra, ewp_ra_params, label="EWP")
    plot_beta_with_point(angle_hse_ra, hse_ra_params, label="HSE")
    plot_beta_with_point(angle_sew_ra, sew_ra_params, label="SEW")
    

    return {
        "Elbow->Wrist->Fingers Score (Right Arm)": score_ewp_ra,
        "Hip->Shoulder->Elbow Score (Right Arm)": score_hse_ra,
        "Shoulder->Elbow->Wrist Score (Right Arm)": score_sew_ra
        
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
    score_sew_la = math.ceil(max(0, min(100, score_sew_la)))
    
    # ewa: Angle at wrist using points: left elbow, wrist, average between thumb and pinky
    pdf_ewa_la_new = beta.pdf(angle_ewa_la/180.0, ewa_la_params["alpha"], ewa_la_params["beta"])
    pdf_ewa_la_mean = beta.pdf(ewa_la_params["mean"]/180.0, ewa_la_params["alpha"], ewa_la_params["beta"])
    score_ewa_la = (pdf_ewa_la_new / pdf_ewa_la_mean) * 100 if pdf_ewa_la_mean != 0 else 0
    score_ewa_la = math.ceil(max(0, min(100, score_ewa_la)))
    
    
    return {
        "Elbow->Wrist->Fingers Score (Left Arm)": score_ewa_la,
        # "Hip->Shoulder->Elbow Score (Left Arm)": score_hse_la,
        "Shoulder->Elbow->Wrist Score (Left Arm)": score_sew_la
        
    }

def get_klay_data():
    Max_Front= {'nose': [983, 520], 'left_eye_inner': [984, 524], 'left_eye': [987, 524], 'left_eye_outer': [989, 524], 'right_eye_inner': [977, 524], 'right_eye': [975, 523], 'right_eye_outer': [972, 523], 'left_ear': [989, 515], 'right_ear': [965, 514], 'left_mouth': [988, 512], 'right_mouth': [979, 512], 'left_shoulder': [1009, 479], 'right_shoulder': [952, 472], 'left_elbow': [1028, 532], 'right_elbow': [961, 529], 'left_wrist': [1014, 594], 'right_wrist': [967, 593], 'left_pinky': [1006, 610], 'right_pinky': [969, 606], 'left_index': [1002, 611], 'right_index': [971, 610], 'left_thumb': [1003, 605], 'right_thumb': [972, 605], 'left_hip': [1010, 354], 'right_hip': [970, 354], 'left_knee': [1028, 259], 'right_knee': [968, 257], 'left_ankle': [1030, 160], 'right_ankle': [942, 157], 'left_heel': [1023, 149], 'right_heel': [932, 146], 'left_foot_index': [1051, 125], 'right_foot_index': [962, 114], 'frame': 39, 'time': 1.2792, 'postion': 'HAND'}
    Eye_Front= {'nose': [1016, 444], 'left_eye_inner': [1019, 452], 'left_eye': [1021, 452], 'left_eye_outer': [1022, 452], 'right_eye_inner': [1012, 452], 'right_eye': [1008, 453], 'right_eye_outer': [1005, 453], 'left_ear': [1021, 449], 'right_ear': [996, 451], 'left_mouth': [1018, 437], 'right_mouth': [1009, 437], 'left_shoulder': [1036, 410], 'right_shoulder': [971, 404], 'left_elbow': [1064, 412], 'right_elbow': [985, 382], 'left_wrist': [1035, 465], 'right_wrist': [1003, 445], 'left_pinky': [1028, 479], 'right_pinky': [1002, 462], 'left_index': [1024, 479], 'right_index': [1000, 462], 'left_thumb': [1025, 473], 'right_thumb': [1000, 455], 'left_hip': [1026, 285], 'right_hip': [988, 284], 'left_knee': [1060, 202], 'right_knee': [992, 192], 'left_ankle': [1051, 122], 'right_ankle': [941, 117], 'left_heel': [1038, 107], 'right_heel': [926, 104], 'left_foot_index': [1076, 93], 'right_foot_index': [962, 82], 'frame': 30, 'time': 0.984, 'postion': 'EYE'}
    Waist_Front= {'nose': [1009, 431], 'left_eye_inner': [1011, 439], 'left_eye': [1014, 438], 'left_eye_outer': [1016, 438], 'right_eye_inner': [1004, 439], 'right_eye': [1001, 439], 'right_eye_outer': [998, 438], 'left_ear': [1020, 433], 'right_ear': [992, 433], 'left_mouth': [1013, 423], 'right_mouth': [1004, 423], 'left_shoulder': [1041, 391], 'right_shoulder': [968, 383], 'left_elbow': [1056, 333], 'right_elbow': [956, 317], 'left_wrist': [1044, 330], 'right_wrist': [1003, 323], 'left_pinky': [1042, 323], 'right_pinky': [1016, 327], 'left_index': [1037, 330], 'right_index': [1017, 335], 'left_thumb': [1035, 332], 'right_thumb': [1012, 334], 'left_hip': [1022, 279], 'right_hip': [982, 279], 'left_knee': [1058, 203], 'right_knee': [989, 195], 'left_ankle': [1052, 120], 'right_ankle': [941, 115], 'left_heel': [1039, 104], 'right_heel': [932, 99], 'left_foot_index': [1075, 93], 'right_foot_index': [962, 81], 'frame': 26, 'time': 0.8528, 'postion': 'WAIST'}
    Max_Side = {'nose': [584, 478], 'left_eye_inner': [579, 484], 'left_eye': [578, 484], 'left_eye_outer': [578, 484], 'right_eye_inner': [577, 483], 'right_eye': [575, 483], 'right_eye_outer': [573, 482], 'left_ear': [570, 479], 'right_ear': [564, 476], 'left_mouth': [584, 470], 'right_mouth': [582, 470], 'left_shoulder': [560, 437], 'right_shoulder': [566, 446], 'left_elbow': None, 'right_elbow': [621, 489], 'left_wrist': None, 'right_wrist': [647, 548], 'left_pinky': None, 'right_pinky': [661, 558], 'left_index': None, 'right_index': [658, 563], 'left_thumb': None, 'right_thumb': [653, 561], 'left_hip': [557, 309], 'right_hip': [573, 310], 'left_knee': None, 'right_knee': [595, 218], 'left_ankle': [581, 122], 'right_ankle': [606, 110], 'left_heel': [570, 106], 'right_heel': [596, 95], 'left_foot_index': [610, 99], 'right_foot_index': [636, 85], 'frame': 24, 'time': 0.7737142857142857, 'postion': 'HAND'}
    Eye_Side = {'nose': [580, 389], 'left_eye_inner': [574, 397], 'left_eye': [573, 397], 'left_eye_outer': [572, 396], 'right_eye_inner': [574, 397], 'right_eye': [573, 397], 'right_eye_outer': [572, 397], 'left_ear': [562, 391], 'right_ear': [562, 390], 'left_mouth': [578, 380], 'right_mouth': [577, 380], 'left_shoulder': [540, 340], 'right_shoulder': [572, 345], 'left_elbow': None, 'right_elbow': [637, 329], 'left_wrist': None, 'right_wrist': [638, 385], 'left_pinky': None, 'right_pinky': [647, 401], 'left_index': None, 'right_index': [629, 401], 'left_thumb': None, 'right_thumb': [627, 395], 'left_hip': [528, 212], 'right_hip': [550, 215], 'left_knee': None, 'right_knee': [609, 137], 'left_ankle': [531, 61], 'right_ankle': [576, 37], 'left_heel': [516, 51], 'right_heel': [564, 23], 'left_foot_index': [553, 32], 'right_foot_index': [608, 23], 'frame': 14, 'time': 0.4513333333333333, 'postion': 'EYE'}
    Waist_Side = {'nose': [587, 382], 'left_eye_inner': [581, 390], 'left_eye': [580, 391], 'left_eye_outer': [578, 391], 'right_eye_inner': [581, 390], 'right_eye': [580, 390], 'right_eye_outer': [579, 390], 'left_ear': [568, 386], 'right_ear': [570, 384], 'left_mouth': [584, 373], 'right_mouth': [583, 373], 'left_shoulder': [528, 339], 'right_shoulder': [574, 343], 'left_elbow': None, 'right_elbow': [558, 271], 'left_wrist': None, 'right_wrist': [610, 251], 'left_pinky': None, 'right_pinky': [622, 244], 'left_index': None, 'right_index': [627, 255], 'left_thumb': None, 'right_thumb': [622, 258], 'left_hip': [512, 219], 'right_hip': [539, 217], 'left_knee': None, 'right_knee': [583, 135], 'left_ankle': [518, 53], 'right_ankle': [568, 30], 'left_heel': [508, 46], 'right_heel': [558, 18], 'left_foot_index': [547, 37], 'right_foot_index': [608, 20], 'frame': 9, 'time': 0.29014285714285715, 'postion': 'WAIST'}
    return Max_Front, Eye_Front, Waist_Front, Max_Side, Eye_Side, Waist_Side

def get_klay_eye_ra_params():
    ewp_ra_params = {'mean': 150.04247767121387, 'std': 12.043310904035549, 'alpha': 24.999145211051367, 'beta': 4.991336203483126}
    hse_ra_params = {'mean': 137.49535255571425, 'std': 6.152654734459472, 'alpha': 117.16357443768788, 'beta': 36.219380016995984}
    sew_ra_params = {'mean': 159.0630767335418, 'std': 5.07095137744814, 'alpha': 113.56221153590216, 'beta': 14.947801574839653}
    return ewp_ra_params, hse_ra_params, sew_ra_params

def main():
    max_f, eye_f, waist_f, max_s, eye_s, waist_s = get_klay_data()
    klay_data = [max_s, eye_s, waist_s]
    klay_data = [max_s]

    ewp_ra_params, hse_ra_params, sew_ra_params = get_klay_eye_ra_params()

    for d in klay_data:
        side_ra_scores = compare_side_ra(d, ewp_ra_params, hse_ra_params, sew_ra_params)
        print(f"side view similarity scores:")
        print(side_ra_scores)
    
if __name__ == "__main__":
    main()